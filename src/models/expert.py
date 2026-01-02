"""Expert model for UnoDigit professionals."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.core.types import JSONType, UUIDType


class Expert(Base):
    """Expert/consultant profile model."""

    __tablename__ = "experts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    calendar_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON fields for flexible data
    specialties: Mapped[list[str]] = mapped_column(JSONType, default=list)
    services: Mapped[list[str]] = mapped_column(JSONType, default=list)
    availability: Mapped[dict] = mapped_column(JSONType, default=dict)

    # OAuth tokens (encrypted)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)

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
