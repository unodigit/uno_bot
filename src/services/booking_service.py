"""Booking service for appointment scheduling and management."""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.booking import Booking
from src.models.session import ConversationSession
from src.models.expert import Expert
from src.schemas.booking import (
    BookingCreate, BookingResponse, AvailabilityResponse, TimeSlot
)
from src.services.calendar_service import CalendarService


class BookingService:
    """Service for managing appointment bookings."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.calendar_service = CalendarService()

    async def get_expert_availability(
        self,
        expert_id: uuid.UUID,
        timezone: Optional[str] = None,
        days_ahead: Optional[int] = None,
        min_slots_to_show: Optional[int] = None
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
                    expert.refresh_token
                )
            except Exception:
                timezone = 'UTC'

        # Use provided or default values
        days_ahead = days_ahead or 14
        min_slots_to_show = min_slots_to_show or 5

        # Get availability from Google Calendar
        time_slots = await self.calendar_service.get_expert_availability(
            refresh_token=expert.refresh_token,
            timezone=timezone,
            days_ahead=days_ahead,
            min_slots_to_show=min_slots_to_show
        )

        # Group slots by date
        slots_by_date = {}
        for slot in time_slots:
            date = slot['date']
            if date not in slots_by_date:
                slots_by_date[date] = []
            slots_by_date[date].append(TimeSlot(**slot))

        return AvailabilityResponse(
            expert_id=expert_id,
            expert_name=expert.name,
            expert_role=expert.role,
            timezone=timezone,
            available_slots=slots_by_date,
            days_ahead=days_ahead,
            min_slots_to_show=min_slots_to_show
        )

    async def create_booking(
        self,
        session_id: uuid.UUID,
        expert_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
        client_name: str,
        client_email: str
    ) -> BookingResponse:
        """Create a new booking and calendar event.

        Args:
            session_id: Conversation session ID
            expert_id: Expert UUID
            start_time: Booking start time
            end_time: Booking end time
            client_name: Client's name
            client_email: Client's email

        Returns:
            Created booking response
        """
        # Get session and expert
        session = await self._get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        expert = await self._get_expert(expert_id)
        if not expert:
            raise ValueError(f"Expert not found: {expert_id}")

        # Check for conflicts
        await self._check_booking_conflicts(
            expert_id, start_time, end_time, exclude_session_id=session_id
        )

        # Create calendar event
        try:
            calendar_event_id = await self.calendar_service.create_calendar_event(
                refresh_token=expert.refresh_token,
                expert_email=expert.email,
                client_name=client_name,
                client_email=client_email,
                start_time=start_time,
                end_time=end_time
            )
        except Exception as e:
            raise Exception(f"Failed to create calendar event: {e}")

        # Create booking record
        booking = Booking(
            session_id=session_id,
            expert_id=expert_id,
            calendar_event_id=calendar_event_id,
            title=f"Consultation with {client_name}",
            start_time=start_time,
            end_time=end_time,
            expert_email=expert.email,
            client_email=client_email,
            client_name=client_name,
            status='confirmed'
        )

        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)

        # Update session with booking ID
        session.booking_id = booking.id
        self.db.add(session)
        await self.db.commit()

        return BookingResponse.from_orm(booking)

    async def get_booking(self, booking_id: uuid.UUID) -> Optional[BookingResponse]:
        """Get a booking by ID."""
        result = await self.db.execute(
            select(Booking)
            .options(selectinload(Booking.session))
            .options(selectinload(Booking.expert))
            .where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()

        if booking:
            return BookingResponse.from_orm(booking)
        return None

    async def get_booking_by_session(self, session_id: uuid.UUID) -> Optional[BookingResponse]:
        """Get booking by session ID."""
        result = await self.db.execute(
            select(Booking)
            .options(selectinload(Booking.session))
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

            # Update calendar event (optional - could delete or mark as cancelled)
            # For now, we'll just update the status in our system

            return True
        except Exception:
            return False

    async def get_expert_bookings(
        self,
        expert_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[BookingResponse]:
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

    async def _get_expert(self, expert_id: uuid.UUID) -> Optional[Expert]:
        """Get expert by ID."""
        result = await self.db.execute(
            select(Expert).where(Expert.id == expert_id)
        )
        return result.scalar_one_or_none()

    async def _get_session(self, session_id: uuid.UUID) -> Optional[ConversationSession]:
        """Get session by ID."""
        result = await self.db.execute(
            select(ConversationSession).where(ConversationSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def _get_booking(self, booking_id: uuid.UUID) -> Optional[Booking]:
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
        exclude_booking_id: Optional[uuid.UUID] = None
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