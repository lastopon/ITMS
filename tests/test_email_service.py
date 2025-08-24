"""
Test email service functionality
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio


class TestEmailService:
    """Test email service functionality"""

    @pytest.fixture
    def email_service(self):
        """Get email service instance"""
        from main import EmailService
        return EmailService()

    @pytest.mark.asyncio
    @patch('main.aiosmtplib.send')
    async def test_send_email_success(self, mock_send, email_service):
        """Test successful email sending"""
        mock_send.return_value = None
        
        result = await email_service.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_body="<p>Test message</p>"
        )
        
        assert result["status"] == "sent"
        assert result["to"] == "test@example.com"
        mock_send.assert_called_once()

    @pytest.mark.asyncio
    @patch('main.aiosmtplib.send')
    async def test_send_email_failure(self, mock_send, email_service):
        """Test email sending failure"""
        mock_send.side_effect = Exception("SMTP Error")
        
        result = await email_service.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_body="<p>Test message</p>"
        )
        
        assert result["status"] == "failed"
        assert result["to"] == "test@example.com"
        assert "error" in result

    @pytest.mark.asyncio
    @patch('main.EmailService.send_email')
    async def test_send_template_email_success(self, mock_send, email_service):
        """Test sending template email"""
        mock_send.return_value = {"status": "sent", "to": "test@example.com"}
        
        template_data = {
            "user_name": "Test User",
            "resource_name": "Meeting Room A",
            "booking_date": "2024-01-15",
            "start_time": "09:00",
            "end_time": "10:00"
        }
        
        result = await email_service.send_template_email(
            to_email="test@example.com",
            template_name="booking_approved",
            data=template_data
        )
        
        assert result["status"] == "sent"
        mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_template_email_invalid_template(self, email_service):
        """Test sending email with invalid template"""
        with pytest.raises(ValueError):
            await email_service.send_template_email(
                to_email="test@example.com",
                template_name="invalid_template",
                data={}
            )

    @pytest.mark.asyncio
    @patch('main.EmailService.send_template_email')
    async def test_send_bulk_email(self, mock_send_template, email_service):
        """Test sending bulk emails"""
        mock_send_template.return_value = {"status": "sent", "to": "test@example.com"}
        
        recipients = ["user1@example.com", "user2@example.com", "user3@example.com"]
        template_data = {"title": "Test", "message": "Bulk email test"}
        
        results = await email_service.send_bulk_email(
            recipients=recipients,
            template_name="system_notification",
            data=template_data
        )
        
        assert len(results) == 3
        assert all(r["status"] == "sent" for r in results)
        assert mock_send_template.call_count == 3


class TestEmailTemplates:
    """Test email template functionality"""

    def test_booking_approved_template(self):
        """Test booking approved template rendering"""
        from main import EMAIL_TEMPLATES
        from jinja2 import Template
        
        template_data = EMAIL_TEMPLATES["booking_approved"]
        html_template = Template(template_data["html_template"])
        
        data = {
            "user_name": "John Doe",
            "resource_name": "Conference Room A",
            "booking_date": "15/01/2024",
            "start_time": "09:00",
            "end_time": "10:00"
        }
        
        rendered = html_template.render(**data)
        assert "John Doe" in rendered
        assert "Conference Room A" in rendered
        assert "15/01/2024" in rendered

    def test_booking_rejected_template(self):
        """Test booking rejected template rendering"""
        from main import EMAIL_TEMPLATES
        from jinja2 import Template
        
        template_data = EMAIL_TEMPLATES["booking_rejected"]
        html_template = Template(template_data["html_template"])
        
        data = {
            "user_name": "Jane Smith",
            "resource_name": "Meeting Room B",
            "booking_date": "16/01/2024",
            "start_time": "14:00",
            "end_time": "15:00",
            "reason": "Room already booked"
        }
        
        rendered = html_template.render(**data)
        assert "Jane Smith" in rendered
        assert "Meeting Room B" in rendered
        assert "Room already booked" in rendered

    def test_system_notification_template(self):
        """Test system notification template rendering"""
        from main import EMAIL_TEMPLATES
        from jinja2 import Template
        
        template_data = EMAIL_TEMPLATES["system_notification"]
        html_template = Template(template_data["html_template"])
        
        data = {
            "title": "System Maintenance",
            "message": "Scheduled maintenance will begin at 2 AM",
            "date": "20/01/2024 14:30:00",
            "notification_type": "Maintenance"
        }
        
        rendered = html_template.render(**data)
        assert "System Maintenance" in rendered
        assert "Scheduled maintenance" in rendered
        assert "20/01/2024" in rendered


class TestEmailConfiguration:
    """Test email configuration"""

    def test_email_config_defaults(self):
        """Test default email configuration"""
        from main import EMAIL_CONFIG
        
        assert EMAIL_CONFIG["smtp_server"] == "localhost"
        assert EMAIL_CONFIG["smtp_port"] == 587
        assert EMAIL_CONFIG["from_email"] == "noreply@itms.local"
        assert EMAIL_CONFIG["use_tls"] == True

    @patch.dict('os.environ', {
        'SMTP_SERVER': 'smtp.gmail.com',
        'SMTP_PORT': '465',
        'SMTP_USERNAME': 'test@gmail.com',
        'FROM_EMAIL': 'test@gmail.com'
    })
    def test_email_config_from_env(self):
        """Test email configuration from environment variables"""
        # Reload the module to pick up new env vars
        import importlib
        import main
        importlib.reload(main)
        
        assert main.EMAIL_CONFIG["smtp_server"] == "smtp.gmail.com"
        assert main.EMAIL_CONFIG["smtp_port"] == 465
        assert main.EMAIL_CONFIG["username"] == "test@gmail.com"
        assert main.EMAIL_CONFIG["from_email"] == "test@gmail.com"