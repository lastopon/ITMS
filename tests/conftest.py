"""
Test configuration and fixtures for ITMS
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Mock user data for testing"""
    return {
        "id": "test-user-123",
        "username": "testuser",
        "email": "test@example.com",
        "role": "admin",
        "permissions": ["read_user", "create_user", "read_notifications", "send_notifications"]
    }


@pytest.fixture
def admin_token():
    """Mock admin token for testing"""
    return "test-admin-token-123"


@pytest.fixture
def user_token():
    """Mock user token for testing"""
    return "test-user-token-456"


@pytest.fixture
def mock_booking():
    """Mock booking data for testing"""
    return {
        "id": "booking-123",
        "resource_id": "resource-456",
        "user_id": "user-789",
        "start_time": "2024-01-15T09:00:00",
        "end_time": "2024-01-15T10:00:00",
        "status": "pending",
        "purpose": "Team meeting",
        "notes": "Test booking"
    }


@pytest.fixture
def mock_notification():
    """Mock notification data for testing"""
    return {
        "id": "notification-123",
        "user_id": "user-456",
        "title": "Test Notification",
        "message": "This is a test notification",
        "type": "info",
        "is_read": False,
        "created_at": "2024-01-15T10:00:00"
    }


@pytest.fixture
def mock_resource():
    """Mock resource data for testing"""
    return {
        "id": "resource-123",
        "name": "Meeting Room A",
        "type": "meeting_room",
        "location": "Building A, Floor 2",
        "capacity": 10,
        "status": "available",
        "features": ["projector", "whiteboard", "video_conference"]
    }