"""Conversation session and message models."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


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
    client_info: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Business context
    business_context: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Qualification data
    qualification: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Lead scoring
    lead_score: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=None
    )
    recommended_service: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )

    # Matched expert
    matched_expert_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experts.id"), nullable=True
    )

    # PRD and booking references
    prd_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    booking_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Tracking
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
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
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    session = relationship("ConversationSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role})>"
