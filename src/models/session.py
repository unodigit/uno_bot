"""Conversation session and message models."""
import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import settings
from src.core.database import Base
from src.core.types import JSONType

# SQLite compatibility
if "sqlite" in settings.database_url:
    INETType = String
    UUID = String  # SQLite stores UUIDs as strings
else:
    from sqlalchemy.dialects.postgresql import INET
    INETType = INET
    UUID = PG_UUID


class SessionStatus(str, Enum):
    """Conversation session status."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SessionPhase(str, Enum):
    """Conversation phase."""

    GREETING = "greeting"
    DISCOVERY = "discovery"
    QUALIFICATION = "qualification"
    PRD_GENERATION = "prd_generation"
    EXPERT_MATCHING = "expert_matching"
    BOOKING = "booking"
    CONFIRMATION = "confirmation"


class MessageRole(str, Enum):
    """Message sender role."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationSession(Base):
    """Conversation session model."""

    __tablename__ = "conversation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    visitor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default=SessionStatus.ACTIVE.value
    )
    current_phase: Mapped[str] = mapped_column(
        String(50), default=SessionPhase.GREETING.value
    )

    # Client information
    client_info: Mapped[dict] = mapped_column(JSONType, default=dict)

    # Business context
    business_context: Mapped[dict] = mapped_column(JSONType, default=dict)

    # Qualification data
    qualification: Mapped[dict] = mapped_column(JSONType, default=dict)

    # Lead scoring
    lead_score: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None
    )
    recommended_service: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    # Matched expert
    matched_expert_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experts.id"), nullable=True
    )

    # PRD and booking references
    prd_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    booking_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Tracking
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INETType, nullable=True)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    matched_expert = relationship("Expert", back_populates="sessions")
    messages = relationship(
        "Message", back_populates="session", order_by="Message.created_at"
    )

    def __repr__(self) -> str:
        return f"<ConversationSession(id={self.id}, status={self.status})>"


class Message(Base):
    """Chat message model."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversation_sessions.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadata for special messages (quick replies, cards, etc.)
    # Note: Using 'meta_data' to avoid SQLAlchemy reserved name 'metadata'
    meta_data: Mapped[dict] = mapped_column(JSONType, default=dict)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    session = relationship("ConversationSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role})>"
