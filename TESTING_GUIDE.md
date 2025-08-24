# ITMS Testing Guide

## Overview

This document describes the comprehensive testing suite for the ITMS (IT Management System). The testing suite includes unit tests, integration tests, and frontend tests to ensure system reliability and functionality.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Test configuration and fixtures
├── test_api_endpoints.py       # API endpoint tests
├── test_email_service.py       # Email service tests
├── test_booking_system.py      # Booking system tests
└── test_frontend.py           # Frontend functionality tests
```

## Test Categories

### 1. Unit Tests (`test_api_endpoints.py`, `test_email_service.py`)
- Test individual functions and methods
- Mock external dependencies
- Fast execution
- High test coverage

**Examples:**
- Authentication endpoints
- User management APIs
- Notification system APIs
- Email template rendering
- Email sending functionality

### 2. Integration Tests (`test_booking_system.py`)
- Test component interactions
- Database operations
- Business logic validation
- Booking workflow tests

**Examples:**
- Booking validation logic
- Conflict detection
- Status management
- Recurring bookings
- Priority handling

### 3. Frontend Tests (`test_frontend.py`)
- UI component testing
- JavaScript function testing
- Form validation
- Responsive design testing
- API integration testing

**Examples:**
- Page loading
- Navigation functionality
- Form submissions
- Mobile responsiveness
- Notification dropdown

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- pytest: Testing framework
- pytest-asyncio: Async test support
- pytest-mock: Mocking utilities
- httpx: HTTP client for API testing
- selenium: Web browser automation

### Test Execution

#### 1. Run All Tests
```bash
python run_tests.py
# or
pytest
```

#### 2. Run Specific Test Categories
```bash
# Unit tests only
python run_tests.py unit

# Integration tests only
python run_tests.py integration

# Frontend tests only
python run_tests.py frontend
```

#### 3. Run Individual Test Files
```bash
# API endpoint tests
pytest tests/test_api_endpoints.py -v

# Email service tests
pytest tests/test_email_service.py -v

# Booking system tests
pytest tests/test_booking_system.py -v

# Frontend tests
pytest tests/test_frontend.py -v
```

#### 4. Generate Coverage Report
```bash
python run_tests.py coverage
# or
pytest --cov=main --cov-report=html tests/
```

### Test Markers

Use markers to run specific test groups:
```bash
# Run only API tests
pytest -m api

# Run only email tests
pytest -m email

# Run only booking tests
pytest -m booking

# Skip frontend tests
pytest -m "not frontend"
```

## Test Fixtures

The test suite uses several fixtures defined in `conftest.py`:

### Client Fixture
```python
@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)
```

### Mock Data Fixtures
- `mock_user`: Sample user data
- `mock_booking`: Sample booking data
- `mock_notification`: Sample notification data
- `mock_resource`: Sample resource data

### Authentication Fixtures
- `admin_token`: Mock admin authentication token
- `user_token`: Mock user authentication token

## Mocking Strategy

The test suite uses extensive mocking to:
- Isolate units under test
- Avoid external dependencies
- Speed up test execution
- Ensure consistent test results

### Example Mocking Patterns

#### API Endpoint Mocking
```python
@patch('main.get_current_user')
@patch('main.check_permission')
def test_get_users_success(self, mock_permission, mock_user, client):
    mock_user.return_value = {"role": "admin"}
    mock_permission.return_value = True
    
    response = client.get("/api/users?token=test-token")
    assert response.status_code == 200
```

#### Async Function Mocking
```python
@pytest.mark.asyncio
@patch('main.aiosmtplib.send')
async def test_send_email_success(self, mock_send, email_service):
    mock_send.return_value = None
    
    result = await email_service.send_email(
        to_email="test@example.com",
        subject="Test",
        html_body="<p>Test</p>"
    )
    
    assert result["status"] == "sent"
```

## Test Data

### Mock Database
Tests use mock database data instead of real database connections:
- In-memory data structures
- Predictable test data
- No database setup required
- Fast test execution

### Sample Data
All test fixtures provide realistic sample data:
- User accounts with different roles
- Booking records with various statuses
- Notifications of different types
- Resources with different properties

## Frontend Testing

### Selenium WebDriver
Frontend tests use mocked Selenium WebDriver to test:
- Page loading and rendering
- JavaScript functionality
- Form interactions
- Navigation behavior
- Responsive design

### JavaScript Testing
Tests verify client-side functionality:
- API calls from frontend
- DOM manipulation
- Event handling
- Form validation
- Local storage operations

## Best Practices

### 1. Test Naming
- Use descriptive test names
- Follow pattern: `test_<action>_<expected_result>`
- Group related tests in classes

### 2. Test Organization
- One test file per major component
- Group related tests in classes
- Use fixtures for common setup

### 3. Assertions
- Use specific assertions
- Test both positive and negative cases
- Include error condition tests

### 4. Mocking
- Mock external dependencies
- Use realistic mock data
- Verify mock interactions when needed

### 5. Test Maintenance
- Keep tests simple and focused
- Update tests when code changes
- Remove obsolete tests

## Continuous Integration

### GitHub Actions (Example)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python run_tests.py
```

### Docker Testing
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "run_tests.py"]
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:."
```

#### 2. Async Test Failures
```bash
# Install pytest-asyncio
pip install pytest-asyncio
```

#### 3. Mock Import Issues
```bash
# Use full module paths in mocks
@patch('main.function_name')
```

#### 4. Selenium Issues
```bash
# Install WebDriver
# Chrome: Download chromedriver
# Firefox: Download geckodriver
```

### Debug Options
```bash
# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Debug prints
pytest -s

# Show local variables on failure
pytest --tb=long
```

## Performance Testing

### Load Testing (Future Enhancement)
Consider adding:
- API endpoint load tests
- Database performance tests
- Concurrent user simulation
- Response time benchmarks

### Tools
- locust: Load testing tool
- ab (Apache Bench): Simple load testing
- pytest-benchmark: Performance benchmarks

## Test Metrics

### Coverage Goals
- Unit tests: > 90% coverage
- Integration tests: > 80% coverage
- Critical paths: 100% coverage

### Test Categories Distribution
- Unit tests: 60-70%
- Integration tests: 20-30%
- Frontend tests: 10-20%

## Reporting

### Test Reports
- HTML coverage reports
- JUnit XML for CI/CD
- Test execution summaries
- Performance metrics

### Example Output
```
================================ test session starts ================================
collected 45 items

tests/test_api_endpoints.py::TestAuthEndpoints::test_health_check PASSED    [ 2%]
tests/test_api_endpoints.py::TestAuthEndpoints::test_login_success PASSED   [ 4%]
tests/test_email_service.py::TestEmailService::test_send_email_success PASSED [ 6%]
...

========================== 45 passed, 0 failed in 12.34s ==========================
```

This testing suite provides comprehensive coverage of the ITMS system, ensuring reliability, maintainability, and quality assurance throughout the development lifecycle.