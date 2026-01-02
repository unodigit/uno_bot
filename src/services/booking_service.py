"""Booking service for appointment scheduling and management."""
import logging
import uuid
from datetime import datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.booking import Booking
from src.models.expert import Expert
from src.models.session import ConversationSession
from src.schemas.booking import (
    AvailabilityResponse,
    BookingResponse,
    TimeSlot,
)
from src.services.calendar_service import CalendarService
from src.services.email_service import EmailService
from src.services.prd_service import PRDService

logger = logging.getLogger(__name__)


class BookingService:
    """Service for managing appointment bookings."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.calendar_service = CalendarService()
        self.email_service = EmailService()

    async def get_expert_availability(
        self,
        expert_id: uuid.UUID,
        timezone: str | None = None,
        days_ahead: int | None = None,
        min_slots_to_show: int | None = None
    ) -> AvailabilityResponse:
        """Get available time slots for an expert.

        Args:
            expert_id: Expert UUID
            timezone: Timezone for availability (defaults to expert's calendar timezone)
            days_ahead: Number of days to look ahead
            min_slots_to_show: Minimum number of slots to return

        Returns:
            AvailabilityResponse with time slots grouped by date
        """
        # Get expert
        expert = await self._get_expert(expert_id)
        if not expert:
            raise ValueError(f"Expert not found: {expert_id}")

        # Get calendar timezone if not provided
        if not timezone:
            try:
                timezone = await self.calendar_service.get_calendar_timezone(
                    expert.refresh_token or ''
                )
            except Exception:
                timezone = 'UTC'

        # Use provided or default values
        days_ahead = days_ahead or 14
        min_slots_to_show = min_slots_to_show or 5

        # Get availability from Google Calendar
        time_slots = await self.calendar_service.get_expert_availability(
            refresh_token=expert.refresh_token or '',
            timezone=timezone,
            days_ahead=days_ahead,
            min_slots_to_show=min_slots_to_show
        )

        # Convert CalendarService format to TimeSlot format
        # CalendarService returns: {start, end, date, time, timezone, start_formatted}
        # TimeSlot expects: {start_time, end_time, timezone, display_time, display_date}
        slots = []
        for slot in time_slots:
            # Parse start time from ISO format
            start_dt = datetime.fromisoformat(slot['start'])
            end_dt = datetime.fromisoformat(slot['end'])

            slots.append(TimeSlot(
                start_time=start_dt,
                end_time=end_dt,
                timezone=slot.get('timezone', timezone),
                display_time=slot.get('time', start_dt.strftime('%H:%M')),
                display_date=slot.get('date', start_dt.strftime('%Y-%m-%d'))
            ))

        return AvailabilityResponse(
            expert_id=expert_id,
            expert_name=expert.name,
            expert_role=expert.role,
            timezone=timezone,
            slots=slots,
            generated_at=datetime.now()
        )

    async def create_booking(
        self,
        session_id: uuid.UUID,
        expert_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
        client_name: str,
        client_email: str,
        timezone: str = "UTC"
    ) -> BookingResponse:
        """Create a new booking and calendar event.

        Args:
            session_id: Conversation session ID
            expert_id: Expert UUID
            start_time: Booking start time
            end_time: Booking end time
            client_name: Client's name
            client_email: Client's email
            timezone: Timezone for the booking

        Returns:
            Created booking response
        """
        logger.info(f"Creating booking: session={session_id}, expert={expert_id}, client={client_name}")

        # Get session and expert
        session = await self._get_session(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            raise ValueError(f"Session not found: {session_id}")

        expert = await self._get_expert(expert_id)
        if not expert:
            logger.error(f"Expert not found: {expert_id}")
            raise ValueError(f"Expert not found: {expert_id}")

        # Check for conflicts
        await self._check_booking_conflicts(
            expert_id, start_time, end_time, exclude_booking_id=None
        )

        # Get PRD content if available (for expert notification)
        prd_content = None
        if session.prd_id:
            prd_service = PRDService(self.db)
            prd = await prd_service.get_prd(session.prd_id)
            if prd:
                prd_content = prd.content_markdown

        # Create calendar event
        try:
            calendar_event_id = await self.calendar_service.create_calendar_event(
                refresh_token=expert.refresh_token or '',
                expert_email=expert.email,
                client_name=client_name,
                client_email=client_email,
                start_time=start_time,
                end_time=end_time,
                timezone=timezone
            )
        except Exception as e:
            raise Exception(f"Failed to create calendar event: {e}") from e

        # Create booking record
        # Generate Google Meet link (mock for now)
        meeting_link = f"https://meet.google.com/mock-{calendar_event_id}" if calendar_event_id else None

        booking = Booking(
            session_id=session_id,
            expert_id=expert_id,
            calendar_event_id=calendar_event_id,
            title=f"Consultation with {client_name}",
            start_time=start_time,
            end_time=end_time,
            timezone=timezone or 'UTC',
            meeting_link=meeting_link,
            expert_email=expert.email,
            client_email=client_email,
            client_name=client_name,
            status='confirmed'
        )

        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)

        logger.info(f"Booking created successfully: {booking.id} for {client_name} with {expert.name}")

        # Update session with booking ID
        session.booking_id = booking.id
        self.db.add(session)
        await self.db.commit()

        # Send email notifications (fire and forget - don't block booking creation)
        # Run in background task
        try:
            # Send confirmation to client
            client_email_sent = await self.email_service.send_booking_confirmation(
                client_email=client_email,
                client_name=client_name,
                expert_name=expert.name,
                expert_role=expert.role,
                start_time=start_time,
                end_time=end_time,
                timezone=timezone,
                meeting_link=meeting_link,
                prd_url=f"/api/v1/prd/{session.prd_id}/download" if session.prd_id else None,
                booking_id=str(booking.id),
                session_id=str(session_id)
            )

            if client_email_sent:
                booking.confirmation_sent_at = datetime.utcnow()
                self.db.add(booking)
                await self.db.commit()

            # Send notification to expert
            await self.email_service.send_expert_notification(
                expert_email=expert.email,
                expert_name=expert.name,
                client_name=client_name,
                client_email=client_email,
                start_time=start_time,
                end_time=end_time,
                timezone=timezone,
                prd_content=prd_content,
                meeting_link=meeting_link
            )

        except Exception as e:
            # Log email error but don't fail the booking
            print(f"Warning: Email notification failed: {e}")

        return BookingResponse.from_orm(booking)

    async def get_booking(self, booking_id: uuid.UUID) -> BookingResponse | None:
        """Get a booking by ID."""
        result = await self.db.execute(
            select(Booking)
            .options(selectinload(Booking.expert))
            .where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()

        if booking:
            return BookingResponse.from_orm(booking)
        return None

    async def get_booking_by_session(self, session_id: uuid.UUID) -> BookingResponse | None:
        """Get booking by session ID."""
        result = await self.db.execute(
            select(Booking)
            .options(selectinload(Booking.expert))
            .where(Booking.session_id == session_id)
        )
        booking = result.scalar_one_or_none()

        if booking:
            return BookingResponse.from_orm(booking)
        return None

    async def cancel_booking(self, booking_id: uuid.UUID) -> bool:
        """Cancel a booking and update calendar event.

        Args:
            booking_id: Booking UUID to cancel

        Returns:
            True if successfully cancelled, False otherwise
        """
        booking = await self._get_booking(booking_id)
        if not booking:
            return False

        try:
            # Update booking status
            booking.status = 'cancelled'
            self.db.add(booking)
            await self.db.commit()

            # Get expert for notification
            expert = await self._get_expert(booking.expert_id)
            expert_name = expert.name if expert else "Expert"

            # Send cancellation email to client
            try:
                await self.email_service.send_cancellation_email(
                    client_email=booking.client_email,
                    client_name=booking.client_name,
                    expert_name=expert_name,
                    start_time=booking.start_time,
                    end_time=booking.end_time,
                    timezone=booking.timezone
                )
            except Exception as e:
                print(f"Warning: Failed to send cancellation email: {e}")

            # Send cancellation notification to expert
            if expert:
                try:
                    await self.email_service.send_expert_cancellation_notification(
                        expert_email=expert.email,
                        expert_name=expert_name,
                        client_name=booking.client_name,
                        client_email=booking.client_email,
                        start_time=booking.start_time,
                        end_time=booking.end_time,
                        timezone=booking.timezone
                    )
                except Exception as e:
                    print(f"Warning: Failed to send expert cancellation notification: {e}")

            # Delete Google Calendar event
            if booking.calendar_event_id and expert and expert.refresh_token:
                try:
                    await self.calendar_service.delete_calendar_event(
                        refresh_token=expert.refresh_token,
                        event_id=booking.calendar_event_id
                    )
                except Exception as e:
                    print(f"Warning: Failed to delete calendar event: {e}")

            return True
        except Exception as e:
            print(f"Error cancelling booking: {e}")
            return False

    async def get_expert_bookings(
        self,
        expert_id: uuid.UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> list[BookingResponse]:
        """Get all bookings for an expert within a date range."""
        query = select(Booking).where(Booking.expert_id == expert_id)

        if start_date:
            query = query.where(Booking.start_time >= start_date)
        if end_date:
            query = query.where(Booking.end_time <= end_date)

        query = query.options(selectinload(Booking.session))

        result = await self.db.execute(query)
        bookings = result.scalars().all()

        return [BookingResponse.from_orm(booking) for booking in bookings]

    async def send_reminder_emails(self, hours_before: int = 24) -> int:
        """Send reminder emails for upcoming bookings.

        Args:
            hours_before: Hours before appointment to send reminder (24 or 1)

        Returns:
            Number of reminder emails sent
        """
        from sqlalchemy import and_

        # Calculate time window
        now = datetime.utcnow()
        start_window = now + timedelta(hours=hours_before)
        end_window = now + timedelta(hours=hours_before + 1)

        # Find bookings that need reminders
        query = select(Booking).where(
            and_(
                Booking.status == 'confirmed',
                Booking.start_time >= start_window,
                Booking.start_time < end_window,
                # Only send once per reminder period
                Booking.reminder_sent_at == None  # noqa: E711
            )
        )

        result = await self.db.execute(query)
        bookings = result.scalars().all()

        sent_count = 0
        for booking in bookings:
            try:
                # Get expert for name
                expert = await self._get_expert(booking.expert_id)
                expert_name = expert.name if expert else "Expert"

                # Send reminder email
                success = await self.email_service.send_reminder_email(
                    client_email=booking.client_email,
                    client_name=booking.client_name,
                    expert_name=expert_name,
                    start_time=booking.start_time,
                    end_time=booking.end_time,
                    timezone=booking.timezone,
                    meeting_link=booking.meeting_link,
                    hours_before=hours_before
                )

                if success:
                    booking.reminder_sent_at = datetime.utcnow()
                    self.db.add(booking)
                    await self.db.commit()
                    sent_count += 1
            except Exception as e:
                print(f"Warning: Failed to send reminder for booking {booking.id}: {e}")

        return sent_count

    async def _get_expert(self, expert_id: uuid.UUID) -> Expert | None:
        """Get expert by ID."""
        result = await self.db.execute(
            select(Expert).where(Expert.id == expert_id)
        )
        return result.scalar_one_or_none()

    async def _get_session(self, session_id: uuid.UUID) -> ConversationSession | None:
        """Get session by ID."""
        result = await self.db.execute(
            select(ConversationSession).where(ConversationSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def _get_booking(self, booking_id: uuid.UUID) -> Booking | None:
        """Get booking by ID."""
        result = await self.db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()

    async def _check_booking_conflicts(
        self,
        expert_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: uuid.UUID | None = None
    ) -> None:
        """Check for booking conflicts within the same expert.

        Args:
            expert_id: Expert UUID
            start_time: Proposed start time
            end_time: Proposed end time
            exclude_booking_id: Booking ID to exclude from conflict check (for updates)

        Raises:
            ValueError: If a conflict is found
        """
        # Check existing bookings in database
        query = select(Booking).where(
            and_(
                Booking.expert_id == expert_id,
                Booking.status == 'confirmed',
                Booking.id != exclude_booking_id,
                # Check for time overlap
                and_(
                    Booking.start_time < end_time,
                    Booking.end_time > start_time
                )
            )
        )

        result = await self.db.execute(query)
        conflicting_bookings = result.scalars().all()

        if conflicting_bookings:
            raise ValueError("Time slot is already booked")

        # Additional check: verify with Google Calendar (optional for now)
        # This could be implemented to check real-time calendar conflicts
