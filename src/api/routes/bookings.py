"""API routes for booking and calendar functionality."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.schemas.booking import (
    BookingCreate, BookingResponse, AvailabilityResponse, TimeSlot
)
from src.schemas.expert import ExpertResponse
from src.services.booking_service import BookingService
# from src.services.calendar_service import CalendarService
from src.services.expert_service import ExpertService
from src.services.session_service import SessionService


router = APIRouter()


@router.get("/experts/{expert_id}/availability", response_model=AvailabilityResponse)
async def get_expert_availability(
    expert_id: UUID,
    timezone: Optional[str] = None,
    days_ahead: Optional[int] = None,
    min_slots_to_show: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get available time slots for an expert.

    Args:
        expert_id: Expert UUID
        timezone: Timezone for availability (defaults to expert's calendar timezone)
        days_ahead: Number of days to look ahead for availability
        min_slots_to_show: Minimum number of slots to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        AvailabilityResponse with grouped time slots
    """
    booking_service = BookingService(db)

    try:
        availability = await booking_service.get_expert_availability(
            expert_id=expert_id,
            timezone=timezone,
            days_ahead=days_ahead,
            min_slots_to_show=min_slots_to_show
        )
        return availability
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get availability: {str(e)}"
        )


@router.post("/sessions/{session_id}/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    session_id: UUID,
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new booking for a session.

    Args:
        session_id: Conversation session ID
        booking_data: Booking creation data including expert_id, start_time, end_time
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created booking response
    """
    booking_service = BookingService(db)

    try:
        booking = await booking_service.create_booking(
            session_id=session_id,
            expert_id=booking_data.expert_id,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            client_name=booking_data.client_name,
            client_email=booking_data.client_email,
            timezone=booking_data.timezone
        )
        return booking
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create booking: {str(e)}"
        )


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a booking by ID.

    Args:
        booking_id: Booking UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Booking response
    """
    booking_service = BookingService(db)

    try:
        booking = await booking_service.get_booking(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        return booking
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get booking: {str(e)}"
        )


@router.get("/sessions/{session_id}/bookings", response_model=Optional[BookingResponse])
async def get_booking_by_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    
):
    """Get booking by session ID.

    Args:
        session_id: Conversation session ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Booking response or None if not found
    """
    booking_service = BookingService(db)

    try:
        booking = await booking_service.get_booking_by_session(session_id)
        return booking
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get booking: {str(e)}"
        )


@router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),

):
    """Cancel a booking.

    Args:
        booking_id: Booking UUID to cancel
        db: Database session
        current_user: Current authenticated user

    Returns:
        Success message
    """
    booking_service = BookingService(db)

    success = await booking_service.cancel_booking(booking_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    return {"message": "Booking cancelled successfully"}


@router.get("/experts/{expert_id}/bookings", response_model=List[BookingResponse])
async def get_expert_bookings(
    expert_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    
):
    """Get all bookings for an expert within a date range.

    Args:
        expert_id: Expert UUID
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of booking responses
    """
    booking_service = BookingService(db)

    try:
        bookings = await booking_service.get_expert_bookings(
            expert_id=expert_id,
            start_date=start_date,
            end_date=end_date
        )
        return bookings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get expert bookings: {str(e)}"
        )