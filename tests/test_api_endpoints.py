"""
Test API endpoints for ITMS
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestAuthEndpoints:
    """Test authentication endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "ITMS API"}

    @patch('main.authenticate_user')
    def test_login_success(self, mock_auth, client):
        """Test successful login"""
        mock_auth.return_value = {
            "username": "testuser",
            "email": "test@example.com",
            "role": "admin"
        }
        
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post("/auth/login", json={
            "username": "invalid",
            "password": "invalid"
        })
        
        assert response.status_code == 401


class TestUserManagement:
    """Test user management endpoints"""

    @patch('main.get_current_user')
    @patch('main.check_permission')
    def test_get_users_success(self, mock_permission, mock_get_user, client, mock_user, admin_token):
        """Test getting users list"""
        mock_user.return_value = mock_user
        mock_permission.return_value = True
        
        response = client.get(f"/api/users?token={admin_token}")
        assert response.status_code == 200
        
    @patch('main.get_current_user')
    @patch('main.check_permission')
    def test_get_users_no_permission(self, mock_permission, mock_user, client, user_token):
        """Test getting users without permission"""
        mock_user.return_value = {"role": "user"}
        mock_permission.return_value = False
        
        response = client.get(f"/api/users?token={user_token}")
        assert response.status_code == 403


class TestBookingSystem:
    """Test booking system endpoints"""

    @patch('main.get_current_user')
    @patch('main.check_permission')
    @patch('main.bookings_db')
    def test_get_bookings(self, mock_db, mock_permission, mock_user, client, admin_token):
        """Test getting bookings"""
        mock_user.return_value = {"username": "testuser", "role": "admin"}
        mock_permission.return_value = True
        mock_db.__iter__.return_value = iter([])
        
        response = client.get(f"/api/bookings?token={admin_token}")
        assert response.status_code == 200

    @patch('main.get_current_user')
    @patch('main.check_permission')
    @patch('main.bookings_db')
    def test_create_booking(self, mock_db, mock_permission, mock_user, client, admin_token, mock_booking):
        """Test creating a booking"""
        mock_user.return_value = {"username": "testuser", "role": "admin"}
        mock_permission.return_value = True
        mock_db.__getitem__ = MagicMock()
        mock_db.__setitem__ = MagicMock()
        
        booking_data = {
            "resource_id": "resource-123",
            "start_time": "2024-01-15T09:00:00",
            "end_time": "2024-01-15T10:00:00",
            "purpose": "Test meeting"
        }
        
        response = client.post(f"/api/bookings?token={admin_token}", json=booking_data)
        assert response.status_code in [200, 201]


class TestNotificationSystem:
    """Test notification system endpoints"""

    @patch('main.get_current_user')
    @patch('main.check_permission')
    @patch('main.notifications_db')
    def test_get_notifications(self, mock_db, mock_permission, mock_user, client, admin_token):
        """Test getting notifications"""
        mock_user.return_value = {"username": "testuser", "role": "admin"}
        mock_permission.return_value = True
        mock_db.__iter__.return_value = iter([])
        
        response = client.get(f"/api/notifications?token={admin_token}")
        assert response.status_code == 200

    @patch('main.get_current_user')
    @patch('main.check_permission')
    @patch('main.notifications_db')
    def test_create_notification(self, mock_db, mock_permission, mock_user, client, admin_token):
        """Test creating a notification"""
        mock_user.return_value = {"username": "testuser", "role": "admin"}
        mock_permission.return_value = True
        mock_db.__setitem__ = MagicMock()
        
        notification_data = {
            "user_id": "user-123",
            "title": "Test Notification",
            "message": "This is a test",
            "type": "info"
        }
        
        response = client.post(f"/api/notifications?token={admin_token}", json=notification_data)
        assert response.status_code in [200, 201]


class TestEmailSystem:
    """Test email system endpoints"""

    @patch('main.get_current_user')
    @patch('main.check_permission')
    @patch('main.email_service')
    def test_send_email(self, mock_service, mock_permission, mock_user, client, admin_token):
        """Test sending email"""
        mock_user.return_value = {"username": "testuser", "role": "admin"}
        mock_permission.return_value = True
        mock_service.send_email.return_value = {"status": "sent", "to": "test@example.com"}
        
        email_data = {
            "to": "test@example.com",
            "subject": "Test Email",
            "body": "Test message",
            "is_html": False
        }
        
        response = client.post(f"/api/email/send?token={admin_token}", json=email_data)
        assert response.status_code == 200

    @patch('main.get_current_user')
    @patch('main.check_permission')
    def test_get_email_templates(self, mock_permission, mock_user, client, admin_token):
        """Test getting email templates"""
        mock_user.return_value = {"username": "testuser", "role": "admin"}
        mock_permission.return_value = True
        
        response = client.get(f"/api/email/templates?token={admin_token}")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data


class TestSystemHealth:
    """Test system health monitoring endpoints"""

    @patch('main.get_current_user')
    @patch('main.check_permission')
    def test_system_health(self, mock_permission, mock_user, client, admin_token):
        """Test system health endpoint"""
        mock_user.return_value = {"username": "testuser", "role": "admin"}
        mock_permission.return_value = True
        
        response = client.get(f"/api/health/system?token={admin_token}")
        assert response.status_code == 200

    @patch('main.get_current_user')
    @patch('main.check_permission')
    def test_performance_metrics(self, mock_permission, mock_user, client, admin_token):
        """Test performance metrics endpoint"""
        mock_user.return_value = {"username": "testuser", "role": "admin"}
        mock_permission.return_value = True
        
        response = client.get(f"/api/health/performance?token={admin_token}")
        assert response.status_code == 200
        
    @patch('main.get_current_user')
    @patch('main.check_permission')
    def test_backup_create(self, mock_permission, mock_user, client, admin_token):
        """Test backup creation endpoint"""
        mock_user.return_value = {"username": "testuser", "role": "admin"}
        mock_permission.return_value = True
        
        response = client.post(f"/api/backup/create?token={admin_token}")
        assert response.status_code == 200


class TestDataExport:
    """Test data export endpoints"""

    @patch('main.get_current_user')
    @patch('main.check_permission')
    def test_export_users(self, mock_permission, mock_user, client, admin_token):
        """Test exporting users data"""
        mock_user.return_value = {"username": "testuser", "role": "admin"}
        mock_permission.return_value = True
        
        response = client.get(f"/api/export/users?format=csv&token={admin_token}")
        assert response.status_code == 200

    @patch('main.get_current_user')
    @patch('main.check_permission')
    def test_export_bookings(self, mock_permission, mock_user, client, admin_token):
        """Test exporting bookings data"""
        mock_user.return_value = {"username": "testuser", "role": "admin"}
        mock_permission.return_value = True
        
        response = client.get(f"/api/export/bookings?format=json&token={admin_token}")
        assert response.status_code == 200