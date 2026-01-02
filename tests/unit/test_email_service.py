"""Unit tests for EmailService."""
import os
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from src.core.config import settings
from src.services.email_service import EmailService


class TestEmailService:
    """Test cases for EmailService."""

    @pytest.fixture
    def email_service(self):
        """Create EmailService instance."""
        return EmailService()

    @pytest.fixture
    def sample_booking_data(self):
        """Sample booking data for testing."""
        return {
            "client_email": "test@example.com",
            "client_name": "Test User",
            "expert_name": "Dr. Jane Smith",
            "expert_role": "AI Strategy Consultant",
            "start_time": datetime(2025, 1, 15, 14, 0),
            "end_time": datetime(2025, 1, 15, 15, 0),
            "timezone": "UTC",
            "meeting_link": "https://meet.google.com/test-meeting",
            "prd_url": "https://example.com/prd/test",
            "booking_id": "booking_123",
            "session_id": "session_456",
        }

    @pytest.fixture
    def sample_reminder_data(self):
        """Sample reminder data for testing."""
        return {
            "client_email": "test@example.com",
            "client_name": "Test User",
            "expert_name": "Dr. Jane Smith",
            "expert_role": "AI Strategy Consultant",
            "start_time": datetime(2025, 1, 15, 14, 0),
            "end_time": datetime(2025, 1, 15, 15, 0),
            "timezone": "UTC",
            "meeting_link": "https://meet.google.com/test-meeting",
            "hours_until": 1,
        }

    def test_init(self, email_service):
        """Test EmailService initialization."""
        assert email_service.api_key == settings.sendgrid_api_key
        assert email_service.from_email == settings.sendgrid_from_email
        assert email_service.environment == settings.environment

    @patch('src.services.email_service.sendgrid.SendGridAPIClient')
    @patch('src.services.email_service.Mail')
    @pytest.mark.asyncio
    async def test_send_booking_confirmation_success(
        self,
        mock_mail,
        mock_sendgrid_client,
        email_service,
        sample_booking_data
    ):
        """Test successful booking confirmation email."""
        # Mock the SendGrid client and response
        mock_client_instance = AsyncMock()
        mock_sendgrid_client.return_value = mock_client_instance
        mock_client_instance.send.return_value.status_code = 202

        # Mock the Mail class
        mock_mail_instance = AsyncMock()
        mock_mail.return_value = mock_mail_instance

        result = await email_service.send_booking_confirmation(**sample_booking_data)

        assert result is True
        mock_mail.assert_called_once()
        mock_client_instance.send.assert_called_once()

    @patch('src.services.email_service.sendgrid.SendGridAPIClient')
    @patch('src.services.email_service.Mail')
    @pytest.mark.asyncio
    async def test_send_booking_confirmation_failure(
        self,
        mock_mail,
        mock_sendgrid_client,
        email_service,
        sample_booking_data
    ):
        """Test booking confirmation email failure."""
        # Mock the SendGrid client to raise an exception
        mock_sendgrid_client.side_effect = Exception("SendGrid API error")

        result = await email_service.send_booking_confirmation(**sample_booking_data)

        assert result is False

    @patch('src.services.email_service.sendgrid.SendGridAPIClient')
    @patch('src.services.email_service.Mail')
    @pytest.mark.asyncio
    async def test_send_booking_confirmation_no_meeting_link(
        self,
        mock_mail,
        mock_sendgrid_client,
        email_service,
        sample_booking_data
    ):
        """Test booking confirmation without meeting link."""
        sample_booking_data["meeting_link"] = None

        mock_client_instance = AsyncMock()
        mock_sendgrid_client.return_value = mock_client_instance
        mock_client_instance.send.return_value.status_code = 202

        mock_mail_instance = AsyncMock()
        mock_mail.return_value = mock_mail_instance

        result = await email_service.send_booking_confirmation(**sample_booking_data)

        assert result is True

    @patch('src.services.email_service.sendgrid.SendGridAPIClient')
    @patch('src.services.email_service.Mail')
    @pytest.mark.asyncio
    async def test_send_booking_confirmation_no_prd(
        self,
        mock_mail,
        mock_sendgrid_client,
        email_service,
        sample_booking_data
    ):
        """Test booking confirmation without PRD URL."""
        sample_booking_data["prd_url"] = None

        mock_client_instance = AsyncMock()
        mock_sendgrid_client.return_value = mock_client_instance
        mock_client_instance.send.return_value.status_code = 202

        mock_mail_instance = AsyncMock()
        mock_mail.return_value = mock_mail_instance

        result = await email_service.send_booking_confirmation(**sample_booking_data)

        assert result is True

    @patch('src.services.email_service.sendgrid.SendGridAPIClient')
    @patch('src.services.email_service.Mail')
    @pytest.mark.asyncio
    async def test_send_booking_confirmation_dev_environment(
        self,
        mock_mail,
        mock_sendgrid_client,
        email_service,
        sample_booking_data
    ):
        """Test booking confirmation in development environment."""
        # Mock dev environment
        with patch.object(settings, 'environment', 'development'):
            result = await email_service.send_booking_confirmation(**sample_booking_data)

            # Should succeed in dev environment
            assert result is True
            # Should not call SendGrid in dev
            mock_sendgrid_client.assert_not_called()

    @patch('src.services.email_service.sendgrid.SendGridAPIClient')
    @patch('src.services.email_service.Mail')
    @pytest.mark.asyncio
    async def test_send_booking_confirmation_prod_no_api_key(
        self,
        mock_mail,
        mock_sendgrid_client,
        email_service,
        sample_booking_data
    ):
        """Test booking confirmation in production without API key."""
        # Mock prod environment without API key
        with patch.object(settings, 'sendgrid_api_key', None):
            with patch.object(settings, 'environment', 'production'):
                result = await email_service.send_booking_confirmation(**sample_booking_data)

                assert result is False
                mock_sendgrid_client.assert_not_called()

    @patch('src.services.email_service.sendgrid.SendGridAPIClient')
    @patch('src.services.email_service.Mail')
    @pytest.mark.asyncio
    async def test_send_expert_notification_success(
        self,
        mock_mail,
        mock_sendgrid_client,
        email_service,
        sample_booking_data
    ):
        """Test successful expert notification email."""
        # Mock the SendGrid client and response
        mock_client_instance = AsyncMock()
        mock_sendgrid_client.return_value = mock_client_instance
        mock_client_instance.send.return_value.status_code = 202

        # Mock the Mail class
        mock_mail_instance = AsyncMock()
        mock_mail.return_value = mock_mail_instance

        expert_email = "expert@example.com"
        result = await email_service.send_expert_notification(
            expert_email=expert_email,
            **sample_booking_data
        )

        assert result is True
        mock_mail.assert_called_once()
        mock_client_instance.send.assert_called_once()

    @patch('src.services.email_service.sendgrid.SendGridAPIClient')
    @patch('src.services.email_service.Mail')
    @pytest.mark.asyncio
    async def test_send_expert_notification_failure(
        self,
        mock_mail,
        mock_sendgrid_client,
        email_service,
        sample_booking_data
    ):
        """Test expert notification email failure."""
        mock_sendgrid_client.side_effect = Exception("SendGrid API error")

        expert_email = "expert@example.com"
        result = await email_service.send_expert_notification(
            expert_email=expert_email,
            **sample_booking_data
        )

        assert result is False

    @patch('src.services.email_service.sendgrid.SendGridAPIClient')
    @patch('src.services.email_service.Mail')
    @pytest.mark.asyncio
    async def test_send_reminder_email_success(
        self,
        mock_mail,
        mock_sendgrid_client,
        email_service,
        sample_reminder_data
    ):
        """Test successful reminder email."""
        mock_client_instance = AsyncMock()
        mock_sendgrid_client.return_value = mock_client_instance
        mock_client_instance.send.return_value.status_code = 202

        mock_mail_instance = AsyncMock()
        mock_mail.return_value = mock_mail_instance

        result = await email_service.send_reminder_email(**sample_reminder_data)

        assert result is True
        mock_mail.assert_called_once()
        mock_client_instance.send.assert_called_once()

    @patch('src.services.email_service.sendgrid.SendGridAPIClient')
    @patch('src.services.email_service.Mail')
    @pytest.mark.asyncio
    async def test_send_reminder_email_failure(
        self,
        mock_mail,
        mock_sendgrid_client,
        email_service,
        sample_reminder_data
    ):
        """Test reminder email failure."""
        mock_sendgrid_client.side_effect = Exception("SendGrid API error")

        result = await email_service.send_reminder_email(**sample_reminder_data)

        assert result is False

    @patch('src.services.email_service.sendgrid.SendGridAPIClient')
    @patch('src.services.email_service.Mail')
    @pytest.mark.asyncio
    async def test_send_reminder_email_1_hour(
        self,
        mock_mail,
        mock_sendgrid_client,
        email_service,
        sample_reminder_data
    ):
        """Test 1-hour reminder email."""
        sample_reminder_data["hours_until"] = 1

        mock_client_instance = AsyncMock()
        mock_sendgrid_client.return_value = mock_client_instance
        mock_client_instance.send.return_value.status_code = 202

        mock_mail_instance = AsyncMock()
        mock_mail.return_value = mock_mail_instance

        result = await email_service.send_reminder_email(**sample_reminder_data)

        assert result is True

    @patch('src.services.email_service.sendgrid.SendGridAPIClient')
    @patch('src.services.email_service.Mail')
    @pytest.mark.asyncio
    async def test_send_reminder_email_24_hours(
        self,
        mock_mail,
        mock_sendgrid_client,
        email_service,
        sample_reminder_data
    ):
        """Test 24-hour reminder email."""
        sample_reminder_data["hours_until"] = 24

        mock_client_instance = AsyncMock()
        mock_sendgrid_client.return_value = mock_client_instance
        mock_client_instance.send.return_value.status_code = 202

        mock_mail_instance = AsyncMock()
        mock_mail.return_value = mock_mail_instance

        result = await email_service.send_reminder_email(**sample_reminder_data)

        assert result is True

    @pytest.mark.asyncio
    async def test_format_date_time(self, email_service):
        """Test date and time formatting."""
        dt = datetime(2025, 1, 15, 14, 30)
        date_str, time_str = email_service._format_date_time(dt, "UTC")

        assert date_str == "Wednesday, January 15, 2025"
        assert time_str == "2:30 PM UTC"

    @pytest.mark.asyncio
    async def test_format_date_time_different_timezone(self, email_service):
        """Test date and time formatting with different timezone."""
        dt = datetime(2025, 1, 15, 14, 30)
        date_str, time_str = email_service._format_date_time(dt, "America/New_York")

        assert date_str == "Wednesday, January 15, 2025"
        assert time_str == "2:30 PM America/New_York"

    def test_get_subject_line(self, email_service):
        """Test subject line generation."""
        subject = email_service._get_subject_line("Dr. Jane Smith", "booking")
        assert "✅ Booking Confirmed" in subject
        assert "Dr. Jane Smith" in subject

        subject = email_service._get_subject_line("Dr. Jane Smith", "reminder_1h")
        assert "⏰ 1 Hour Reminder" in subject
        assert "Dr. Jane Smith" in subject

        subject = email_service._get_subject_line("Dr. Jane Smith", "reminder_24h")
        assert "⏰ 24 Hour Reminder" in subject
        assert "Dr. Jane Smith" in subject

    def test_get_subject_line_expert(self, email_service):
        """Test expert notification subject line."""
        subject = email_service._get_subject_line_expert("Test User", "booking")
        assert "✅ New Booking Request" in subject
        assert "Test User" in subject

    def test_format_meeting_link(self, email_service):
        """Test meeting link formatting."""
        link = "https://meet.google.com/test-meeting"
        formatted = email_service._format_meeting_link(link)
        assert formatted == (
            '<a href="https://meet.google.com/test-meeting" '
            'style="color: #2563EB; text-decoration: none; font-weight: 600;">'
            'Join Meeting</a>'
        )

    def test_format_meeting_link_none(self, email_service):
        """Test meeting link formatting with None."""
        formatted = email_service._format_meeting_link(None)
        assert formatted == "Meeting link will be provided before the call"

    def test_get_environment_note(self, email_service):
        """Test environment note generation."""
        with patch.object(settings, 'environment', 'development'):
            note = email_service._get_environment_note()
            assert "This is a test email from the development environment" in note

        with patch.object(settings, 'environment', 'production'):
            note = email_service._get_environment_note()
            assert note == ""

    def test_check_email_config(self, email_service):
        """Test email configuration check."""
        # Test with API key
        with patch.object(settings, 'sendgrid_api_key', "test_key"):
            assert email_service._check_email_config() is True

        # Test without API key
        with patch.object(settings, 'sendgrid_api_key', None):
            assert email_service._check_email_config() is False

        # Test with empty API key
        with patch.object(settings, 'sendgrid_api_key', ""):
            assert email_service._check_email_config() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])