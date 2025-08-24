#!/usr/bin/env python3
"""
Test runner script for ITMS
Usage: python run_tests.py [options]
"""

import sys
import pytest
import subprocess
import os
from pathlib import Path


def check_dependencies():
    """Check if all test dependencies are installed"""
    try:
        import pytest
        import httpx
        import selenium
        print("✅ All test dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing test dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False


def run_unit_tests():
    """Run unit tests"""
    print("\n🧪 Running Unit Tests...")
    return pytest.main([
        "tests/test_api_endpoints.py",
        "tests/test_email_service.py",
        "-m", "not frontend",
        "-v"
    ])


def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running Integration Tests...")
    return pytest.main([
        "tests/test_booking_system.py",
        "-v"
    ])


def run_frontend_tests():
    """Run frontend tests"""
    print("\n🌐 Running Frontend Tests...")
    print("Note: Frontend tests use mocked Selenium WebDriver")
    return pytest.main([
        "tests/test_frontend.py",
        "-v"
    ])


def run_all_tests():
    """Run all tests"""
    print("\n🚀 Running All Tests...")
    return pytest.main([
        "tests/",
        "-v",
        "--tb=short"
    ])


def generate_coverage_report():
    """Generate test coverage report"""
    print("\n📊 Generating Coverage Report...")
    try:
        subprocess.run([
            "pytest",
            "--cov=main",
            "--cov-report=html",
            "--cov-report=term",
            "tests/"
        ], check=True)
        print("📄 Coverage report generated in htmlcov/index.html")
    except subprocess.CalledProcessError:
        print("❌ Failed to generate coverage report")
        print("Install pytest-cov: pip install pytest-cov")


def main():
    """Main test runner"""
    if not check_dependencies():
        sys.exit(1)

    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "unit":
            exit_code = run_unit_tests()
        elif test_type == "integration":
            exit_code = run_integration_tests()
        elif test_type == "frontend":
            exit_code = run_frontend_tests()
        elif test_type == "coverage":
            generate_coverage_report()
            exit_code = 0
        elif test_type in ["all", "full"]:
            exit_code = run_all_tests()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available options: unit, integration, frontend, coverage, all")
            sys.exit(1)
    else:
        # Run all tests by default
        exit_code = run_all_tests()
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        
    sys.exit(exit_code)


if __name__ == "__main__":
    main()