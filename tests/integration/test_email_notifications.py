"""Integration tests for email notification functionality."""
from datetime import datetime, timedelta

import pytest

from src.services.email_service import EmailService


@pytest.mark.asyncio
class TestEmailNotifications:
    """Test email notification functionality."""

    async def test_email_service_send_confirmation(self):
        """Test that email service can send booking confirmation."""
        email_service = EmailService()

        # Test data
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)

        # In development mode, emails are logged not sent
        result = await email_service.send_booking_confirmation(
            client_email="test@example.com",
            client_name="Test Client",
            expert_name="Dr. Expert",
            expert_role="Senior Consultant",
            start_time=start_time,
            end_time=end_time,
            timezone="UTC",
            meeting_link="https://meet.google.com/test",
            prd_url="/api/v1/prd/test-id/download",
            booking_id="test-booking-id"
        )

        # In development mode, it should return True without actually sending
        assert result is True

    async def test_email_service_send_reminder(self):
        """Test that email service can send 24-hour reminder emails."""
        email_service = EmailService()

        start_time = datetime.utcnow() + timedelta(hours=25)
        end_time = start_time + timedelta(hours=1)

        result = await email_service.send_reminder_email(
            client_email="test@example.com",
            client_name="Test Client",
            expert_name="Dr. Expert",
            start_time=start_time,
            end_time=end_time,
            timezone="UTC",
            meeting_link="https://meet.google.com/test",
            hours_before=24
        )

        assert result is True

    async def test_email_service_send_1hour_reminder(self):
        """Test that email service can send 1-hour reminder emails."""
        email_service = EmailService()

        start_time = datetime.utcnow() + timedelta(hours=2)
        end_time = start_time + timedelta(hours=1)

        result = await email_service.send_reminder_email(
            client_email="test@example.com",
            client_name="Test Client",
            expert_name="Dr. Expert",
            start_time=start_time,
            end_time=end_time,
            timezone="UTC",
            meeting_link="https://meet.google.com/test",
            hours_before=1
        )

        assert result is True

    async def test_email_service_send_expert_notification(self):
        """Test that email service can send expert notifications."""
        email_service = EmailService()

        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)

        result = await email_service.send_expert_notification(
            expert_email="expert@example.com",
            expert_name="Dr. Expert",
            client_name="Test Client",
            client_email="test@example.com",
            start_time=start_time,
            end_time=end_time,
            timezone="UTC",
            prd_content="# Project Requirements\n\n- Feature 1\n- Feature 2",
            meeting_link="https://meet.google.com/test"
        )

        assert result is True

    async def test_email_service_ics_generation(self):
        """Test that ICS calendar file is generated correctly."""
        email_service = EmailService()

        start_time = datetime(2025, 1, 15, 14, 0, 0)
        end_time = datetime(2025, 1, 15, 15, 0, 0)

        ics_content = email_service._generate_ics_file(
            summary="Test Meeting",
            description="Test Description",
            start_time=start_time,
            end_time=end_time,
            timezone="UTC",
            location="https://meet.google.com/test",
            uid="test-uid-123"
        )

        assert "BEGIN:VCALENDAR" in ics_content
        assert "BEGIN:VEVENT" in ics_content
        assert "SUMMARY:Test Meeting" in ics_content
        assert "UID:test-uid-123" in ics_content
        assert "DTSTART;TZID=UTC:20250115T140000" in ics_content
        assert "DTEND;TZID=UTC:20250115T150000" in ics_content

    async def test_email_service_send_cancellation(self):
        """Test that email service can send cancellation emails."""
        email_service = EmailService()

        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)

        result = await email_service.send_cancellation_email(
            client_email="test@example.com",
            client_name="Test Client",
            expert_name="Dr. Expert",
            start_time=start_time,
            end_time=end_time,
            timezone="UTC"
        )

        assert result is True
