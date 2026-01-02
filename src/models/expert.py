"""Expert model for UnoDigit professionals."""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Expert(Base):
    """Expert/consultant profile model."""

    __tablename__ = "experts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    calendar_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # JSONB fields for flexible data
    specialties: Mapped[List[str]] = mapped_column(JSONB, default=list)
    services: Mapped[List[str]] = mapped_column(JSONB, default=list)
    availability: Mapped[dict] = mapped_column(JSONB, default=dict)

    # OAuth tokens (encrypted)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    sessions = relationship("ConversationSession", back_populates="matched_expert")
    bookings = relationship("Booking", back_populates="expert")

    def __repr__(self) -> str:
        return f"<Expert(id={self.id}, name={self.name}, role={self.role})>"
