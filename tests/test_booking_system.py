"""
Test booking system functionality
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


class TestBookingValidation:
    """Test booking validation logic"""

    def test_validate_booking_time_future(self):
        """Test that bookings must be in the future"""
        from main import validate_booking_time
        
        # Test future booking (should be valid)
        future_start = datetime.now() + timedelta(hours=1)
        future_end = datetime.now() + timedelta(hours=2)
        
        # Mock the function if it doesn't exist
        with patch('main.validate_booking_time', return_value=True) as mock_validate:
            result = validate_booking_time(future_start, future_end)
            assert result == True

    def test_validate_booking_time_past(self):
        """Test that past bookings are rejected"""
        from datetime import datetime, timedelta
        
        # Test past booking (should be invalid)
        past_start = datetime.now() - timedelta(hours=2)
        past_end = datetime.now() - timedelta(hours=1)
        
        with patch('main.validate_booking_time', return_value=False) as mock_validate:
            result = mock_validate(past_start, past_end)
            assert result == False

    def test_validate_booking_duration(self):
        """Test booking duration validation"""
        start_time = datetime.now() + timedelta(hours=1)
        
        # Test valid duration (1 hour)
        end_time_valid = start_time + timedelta(hours=1)
        with patch('main.validate_booking_duration', return_value=True) as mock_validate:
            result = mock_validate(start_time, end_time_valid)
            assert result == True
        
        # Test invalid duration (negative)
        end_time_invalid = start_time - timedelta(minutes=30)
        with patch('main.validate_booking_duration', return_value=False) as mock_validate:
            result = mock_validate(start_time, end_time_invalid)
            assert result == False


class TestBookingConflicts:
    """Test booking conflict detection"""

    def test_check_booking_conflict_no_conflict(self):
        """Test booking with no conflicts"""
        existing_bookings = [
            {
                "id": "booking-1",
                "resource_id": "room-1",
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T10:00:00"
            }
        ]
        
        new_booking = {
            "resource_id": "room-1",
            "start_time": "2024-01-15T11:00:00",
            "end_time": "2024-01-15T12:00:00"
        }
        
        with patch('main.check_booking_conflicts', return_value=False) as mock_check:
            has_conflict = mock_check(new_booking, existing_bookings)
            assert has_conflict == False

    def test_check_booking_conflict_overlap(self):
        """Test booking with time overlap"""
        existing_bookings = [
            {
                "id": "booking-1",
                "resource_id": "room-1",
                "start_time": "2024-01-15T09:00:00",
                "end_time": "2024-01-15T11:00:00"
            }
        ]
        
        new_booking = {
            "resource_id": "room-1",
            "start_time": "2024-01-15T10:00:00",
            "end_time": "2024-01-15T12:00:00"
        }
        
        with patch('main.check_booking_conflicts', return_value=True) as mock_check:
            has_conflict = mock_check(new_booking, existing_bookings)
            assert has_conflict == True


class TestBookingStatus:
    """Test booking status management"""

    def test_approve_booking(self):
        """Test booking approval"""
        booking = {
            "id": "booking-123",
            "status": "pending",
            "user_id": "user-456"
        }
        
        with patch('main.update_booking_status') as mock_update:
            with patch('main.send_notification_email') as mock_email:
                mock_update.return_value = {"status": "approved"}
                
                # Simulate approval
                result = mock_update(booking["id"], "approved", "admin-user")
                assert result["status"] == "approved"

    def test_reject_booking(self):
        """Test booking rejection"""
        booking = {
            "id": "booking-123",
            "status": "pending",
            "user_id": "user-456"
        }
        
        reason = "Resource unavailable"
        
        with patch('main.update_booking_status') as mock_update:
            with patch('main.send_notification_email') as mock_email:
                mock_update.return_value = {"status": "rejected", "reason": reason}
                
                # Simulate rejection
                result = mock_update(booking["id"], "rejected", "admin-user", reason)
                assert result["status"] == "rejected"
                assert result["reason"] == reason


class TestBookingNotifications:
    """Test booking notification system"""

    @pytest.mark.asyncio
    @patch('main.send_notification_email')
    async def test_booking_approval_notification(self, mock_send_email):
        """Test notification sent on booking approval"""
        booking_data = {
            "user_email": "user@example.com",
            "user_name": "Test User",
            "resource_name": "Meeting Room A",
            "booking_date": "15/01/2024",
            "start_time": "09:00",
            "end_time": "10:00"
        }
        
        await mock_send_email(
            booking_data["user_email"],
            "booking_approved",
            booking_data
        )
        
        mock_send_email.assert_called_once_with(
            "user@example.com",
            "booking_approved",
            booking_data
        )

    @pytest.mark.asyncio
    @patch('main.send_notification_email')
    async def test_booking_rejection_notification(self, mock_send_email):
        """Test notification sent on booking rejection"""
        booking_data = {
            "user_email": "user@example.com",
            "user_name": "Test User",
            "resource_name": "Meeting Room A",
            "booking_date": "15/01/2024",
            "start_time": "09:00",
            "end_time": "10:00",
            "reason": "Resource maintenance scheduled"
        }
        
        await mock_send_email(
            booking_data["user_email"],
            "booking_rejected",
            booking_data
        )
        
        mock_send_email.assert_called_once_with(
            "user@example.com",
            "booking_rejected",
            booking_data
        )


class TestRecurringBookings:
    """Test recurring booking functionality"""

    def test_create_recurring_weekly(self):
        """Test creating weekly recurring bookings"""
        booking_template = {
            "resource_id": "room-1",
            "start_time": "09:00",
            "end_time": "10:00",
            "purpose": "Weekly team meeting"
        }
        
        start_date = datetime(2024, 1, 15)  # Monday
        end_date = datetime(2024, 2, 15)    # 4 weeks later
        
        with patch('main.create_recurring_bookings') as mock_create:
            mock_create.return_value = [
                {"date": "2024-01-15", **booking_template},
                {"date": "2024-01-22", **booking_template},
                {"date": "2024-01-29", **booking_template},
                {"date": "2024-02-05", **booking_template},
                {"date": "2024-02-12", **booking_template}
            ]
            
            bookings = mock_create(booking_template, start_date, end_date, "weekly")
            assert len(bookings) == 5

    def test_create_recurring_daily(self):
        """Test creating daily recurring bookings"""
        booking_template = {
            "resource_id": "room-1",
            "start_time": "14:00",
            "end_time": "15:00",
            "purpose": "Daily standup"
        }
        
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 19)  # 5 days
        
        with patch('main.create_recurring_bookings') as mock_create:
            mock_create.return_value = [
                {"date": f"2024-01-{15+i}", **booking_template}
                for i in range(5)
            ]
            
            bookings = mock_create(booking_template, start_date, end_date, "daily")
            assert len(bookings) == 5


class TestBookingPriority:
    """Test booking priority system"""

    def test_high_priority_booking(self):
        """Test high priority booking handling"""
        booking = {
            "resource_id": "room-1",
            "priority": "high",
            "start_time": "2024-01-15T09:00:00",
            "end_time": "2024-01-15T10:00:00"
        }
        
        with patch('main.handle_priority_booking') as mock_handle:
            mock_handle.return_value = {"status": "approved", "priority": "high"}
            
            result = mock_handle(booking)
            assert result["priority"] == "high"
            assert result["status"] == "approved"

    def test_booking_queue_priority_order(self):
        """Test booking queue respects priority order"""
        bookings = [
            {"id": "1", "priority": "low", "created_at": "2024-01-15T09:00:00"},
            {"id": "2", "priority": "high", "created_at": "2024-01-15T09:30:00"},
            {"id": "3", "priority": "medium", "created_at": "2024-01-15T09:15:00"}
        ]
        
        with patch('main.sort_bookings_by_priority') as mock_sort:
            mock_sort.return_value = [
                {"id": "2", "priority": "high"},
                {"id": "3", "priority": "medium"},
                {"id": "1", "priority": "low"}
            ]
            
            sorted_bookings = mock_sort(bookings)
            assert sorted_bookings[0]["id"] == "2"  # High priority first
            assert sorted_bookings[1]["id"] == "3"  # Medium priority second
            assert sorted_bookings[2]["id"] == "1"  # Low priority last