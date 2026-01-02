"""Booking model for appointment scheduling."""
import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.core.types import UUIDType


class BookingStatus(str, Enum):
    """Booking status."""

    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class Booking(Base):
    """Appointment booking model."""

    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("conversation_sessions.id"), nullable=False
    )
    expert_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("experts.id"), nullable=False
    )

    # Google Calendar reference
    calendar_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Meeting details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    timezone: Mapped[str] = mapped_column(String(100), default="UTC")

    # Meeting link
    meeting_link: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Participant info
    expert_email: Mapped[str] = mapped_column(String(255), nullable=False)
    client_email: Mapped[str] = mapped_column(String(255), nullable=False)
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default=BookingStatus.CONFIRMED.value
    )

    # Email tracking
    confirmation_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reminder_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    expert = relationship("Expert", back_populates="bookings")

    def __repr__(self) -> str:
        return f"<Booking(id={self.id}, status={self.status})>"

    @property
    def is_past(self) -> bool:
        """Check if booking is in the past."""
        return datetime.utcnow() > self.end_time

    @property
    def duration_minutes(self) -> int:
        """Get booking duration in minutes."""
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)
