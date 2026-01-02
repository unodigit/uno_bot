"""Booking schemas for API validation."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TimeSlot(BaseModel):
    """Available time slot."""

    start_time: datetime
    end_time: datetime
    timezone: str
    display_time: str = Field(..., description="Human-readable time display")
    display_date: str = Field(..., description="Human-readable date display")


class AvailabilityRequest(BaseModel):
    """Request schema for fetching availability."""

    expert_id: UUID
    timezone: str = "UTC"
    days_ahead: int = Field(default=14, ge=1, le=30)


class AvailabilityResponse(BaseModel):
    """Response schema for availability data."""

    expert_id: UUID
    expert_name: str
    expert_role: str | None = None
    timezone: str
    slots: list[TimeSlot]
    generated_at: datetime


class BookingCreate(BaseModel):
    """Request schema for creating a booking."""

    expert_id: UUID
    start_time: datetime
    end_time: datetime
    timezone: str = "UTC"
    client_name: str = Field(..., min_length=1, max_length=255)
    client_email: EmailStr


class BookingResponse(BaseModel):
    """Response schema for booking data."""

    id: UUID
    session_id: UUID
    expert_id: UUID
    calendar_event_id: str | None = None
    title: str
    start_time: datetime
    end_time: datetime
    timezone: str
    meeting_link: str | None = None
    expert_email: str
    client_email: str
    client_name: str
    status: str
    confirmation_sent_at: datetime | None = None
    reminder_sent_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingConfirmation(BaseModel):
    """Booking confirmation for chat display."""

    id: UUID
    expert_name: str
    expert_role: str
    date_display: str
    time_display: str
    timezone: str
    meeting_link: str | None = None
    calendar_invite_url: str | None = None


class BookingCancelRequest(BaseModel):
    """Request schema for cancelling a booking."""

    reason: str | None = None
