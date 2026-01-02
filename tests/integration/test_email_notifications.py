"""Integration tests for email notification functionality."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.email_service import EmailService
from src.services.booking_service import BookingService
from src.models.booking import Booking
from src.models.expert import Expert
from src.models.session import ConversationSession


@pytest.mark.asyncio
class TestEmailNotifications:
    """Test email notification functionality."""

    async def test_email_service_send_confirmation(self):
        """Test that email service can send booking confirmation."""
        email_service = EmailService()

        # Test data
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)

        # Mock the SendGrid client
        with patch('src.services.email_service.SendGridAPIClient') as mock_sg:
            mock_response = AsyncMock()
            mock_response.status_code = 202
            mock_sg.return_value.send.return_value = mock_response

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
        """Test that email service can send reminder emails."""
        email_service = EmailService()

        start_time = datetime.utcnow() + timedelta(hours=25)
        end_time = start_time + timedelta(hours=1)

        with patch('src.services.email_service.SendGridAPIClient') as mock_sg:
            mock_response = AsyncMock()
            mock_response.status_code = 202
            mock_sg.return_value.send.return_value = mock_response

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

    async def test_email_service_send_expert_notification(self):
        """Test that email service can send expert notifications."""
        email_service = EmailService()

        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)

        with patch('src.services.email_service.SendGridAPIClient') as mock_sg:
            mock_response = AsyncMock()
            mock_response.status_code = 202
            mock_sg.return_value.send.return_value = mock_response

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

    async def test_booking_service_sends_emails(self):
        """Test that booking service sends emails when creating a booking."""
        # This test verifies the integration but doesn't actually send emails
        # since we're in development mode

        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        from sqlalchemy.orm import sessionmaker
        from src.core.database import Base

        # Create in-memory test database
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session_maker() as session:
            # Create test expert
            expert = Expert(
                name="Dr. Test Expert",
                email="expert@test.com",
                role="Consultant",
                refresh_token="test-token"
            )
            session.add(expert)
            await session.commit()

            # Create test session
            test_session = ConversationSession(
                client_info={"name": "Test Client", "email": "client@test.com"},
                business_context={"challenges": "Test challenge"},
                matched_expert_id=expert.id
            )
            session.add(test_session)
            await session.commit()

            # Create booking service
            booking_service = BookingService(session)

            # Mock email service methods to verify they're called
            with patch.object(booking_service.email_service, 'send_booking_confirmation', new_callable=AsyncMock) as mock_client_email, \
                 patch.object(booking_service.email_service, 'send_expert_notification', new_callable=AsyncMock) as mock_expert_email:

                mock_client_email.return_value = True
                mock_expert_email.return_value = True

                start_time = datetime.utcnow() + timedelta(days=1)
                end_time = start_time + timedelta(hours=1)

                # Create booking
                booking = await booking_service.create_booking(
                    session_id=test_session.id,
                    expert_id=expert.id,
                    start_time=start_time,
                    end_time=end_time,
                    client_name="Test Client",
                    client_email="client@test.com",
                    timezone="UTC"
                )

                # Verify emails were attempted to be sent
                assert mock_client_email.called
                assert mock_expert_email.called

                # Verify booking was created
                assert booking is not None
                assert booking.client_name == "Test Client"

        await engine.dispose()

    async def test_reminder_service(self):
        """Test that reminder service finds and processes bookings correctly."""
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        from sqlalchemy.orm import sessionmaker
        from src.core.database import Base

        # Create in-memory test database
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session_maker() as session:
            # Create test expert
            expert = Expert(
                name="Dr. Test Expert",
                email="expert@test.com",
                role="Consultant",
                refresh_token="test-token"
            )
            session.add(expert)
            await session.commit()

            # Create test session
            test_session = ConversationSession(
                client_info={"name": "Test Client", "email": "client@test.com"},
                business_context={"challenges": "Test challenge"}
            )
            session.add(test_session)
            await session.commit()

            # Create bookings at different times
            now = datetime.utcnow()

            # Booking 24 hours from now (should get 24h reminder)
            booking_24h = Booking(
                session_id=test_session.id,
                expert_id=expert.id,
                title="Test Booking 24h",
                start_time=now + timedelta(hours=24),
                end_time=now + timedelta(hours=25),
                timezone="UTC",
                meeting_link="https://meet.google.com/test",
                expert_email="expert@test.com",
                client_email="client@test.com",
                client_name="Test Client",
                status="confirmed"
            )
            session.add(booking_24h)

            # Booking 1 hour from now (should get 1h reminder)
            booking_1h = Booking(
                session_id=test_session.id,
                expert_id=expert.id,
                title="Test Booking 1h",
                start_time=now + timedelta(hours=1),
                end_time=now + timedelta(hours=2),
                timezone="UTC",
                meeting_link="https://meet.google.com/test",
                expert_email="expert@test.com",
                client_email="client@test.com",
                client_name="Test Client",
                status="confirmed"
            )
            session.add(booking_1h)

            # Booking in 30 hours (should NOT get reminder)
            booking_30h = Booking(
                session_id=test_session.id,
                expert_id=expert.id,
                title="Test Booking 30h",
                start_time=now + timedelta(hours=30),
                end_time=now + timedelta(hours=31),
                timezone="UTC",
                meeting_link="https://meet.google.com/test",
                expert_email="expert@test.com",
                client_email="client@test.com",
                client_name="Test Client",
                status="confirmed"
            )
            session.add(booking_30h)

            await session.commit()

            # Create booking service
            booking_service = BookingService(session)

            # Mock email service
            with patch.object(booking_service.email_service, 'send_reminder_email', new_callable=AsyncMock) as mock_reminder:
                mock_reminder.return_value = True

                # Send 24h reminders
                count_24h = await booking_service.send_reminder_emails(hours_before=24)
                assert count_24h == 1  # Only booking_24h should get this reminder

                # Send 1h reminders
                count_1h = await booking_service.send_reminder_emails(hours_before=1)
                assert count_1h == 1  # Only booking_1h should get this reminder

                # Verify reminder_sent_at was updated
                await session.refresh(booking_24h)
                await session.refresh(booking_1h)
                assert booking_24h.reminder_sent_at is not None
                assert booking_1h.reminder_sent_at is not None

        await engine.dispose()

    async def test_double_booking_prevention(self):
        """Test that double booking prevention works correctly."""
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        from sqlalchemy.orm import sessionmaker
        from src.core.database import Base

        # Create in-memory test database
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session_maker() as session:
            # Create test expert
            expert = Expert(
                name="Dr. Test Expert",
                email="expert@test.com",
                role="Consultant",
                refresh_token="test-token"
            )
            session.add(expert)
            await session.commit()

            # Create test sessions
            session1 = ConversationSession(
                client_info={"name": "Client 1", "email": "client1@test.com"},
                business_context={"challenges": "Test"}
            )
            session2 = ConversationSession(
                client_info={"name": "Client 2", "email": "client2@test.com"},
                business_context={"challenges": "Test"}
            )
            session.add(session1)
            session.add(session2)
            await session.commit()

            # Create first booking
            start_time = datetime.utcnow() + timedelta(days=1)
            end_time = start_time + timedelta(hours=1)

            booking_service = BookingService(session)

            # Mock calendar and email services
            with patch.object(booking_service.calendar_service, 'create_calendar_event', new_callable=AsyncMock) as mock_calendar, \
                 patch.object(booking_service.email_service, 'send_booking_confirmation', new_callable=AsyncMock) as mock_email, \
                 patch.object(booking_service.email_service, 'send_expert_notification', new_callable=AsyncMock) as mock_expert_email:

                mock_calendar.return_value = "mock-event-1"
                mock_email.return_value = True
                mock_expert_email.return_value = True

                # Create first booking
                booking1 = await booking_service.create_booking(
                    session_id=session1.id,
                    expert_id=expert.id,
                    start_time=start_time,
                    end_time=end_time,
                    client_name="Client 1",
                    client_email="client1@test.com",
                    timezone="UTC"
                )

                assert booking1 is not None

                # Try to create overlapping booking - should fail
                with pytest.raises(ValueError, match="Time slot is already booked"):
                    await booking_service.create_booking(
                        session_id=session2.id,
                        expert_id=expert.id,
                        start_time=start_time + timedelta(minutes=30),  # Overlaps
                        end_time=end_time,
                        client_name="Client 2",
                        client_email="client2@test.com",
                        timezone="UTC"
                    )

        await engine.dispose()
