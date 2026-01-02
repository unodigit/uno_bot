"""Welcome message template models."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.core.types import JSONType, UUIDType


class WelcomeMessageTemplate(Base):
    """Welcome message template model for configurable welcome messages."""

    __tablename__ = "welcome_message_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, primary_key=True, default=uuid.uuid4
    )

    # Template name for admin identification
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # The actual welcome message content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Template metadata
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Industry targeting - if specified, this template is preferred for that industry
    target_industry: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Use count - tracks how many times this template has been used
    use_count: Mapped[int] = mapped_column(Integer, default=0)

    # Is this the default template?
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Is this template active?
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Additional configuration (e.g., tone, style, custom variables)
    config: Mapped[dict] = mapped_column(JSONType, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<WelcomeMessageTemplate(id={self.id}, name='{self.name}')>"
