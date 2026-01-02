"""PRD (Project Requirements Document) model."""
import uuid
from datetime import datetime, timedelta

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import settings
from src.core.database import Base
from src.core.types import UUIDType


def default_expiry() -> datetime:
    """Calculate default expiry date (90 days from now)."""
    return datetime.utcnow() + timedelta(days=settings.prd_expiry_days)


class PRDDocument(Base):
    """Project Requirements Document model."""

    __tablename__ = "prd_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType, ForeignKey("conversation_sessions.id"), nullable=False
    )

    # Version tracking
    version: Mapped[int] = mapped_column(Integer, default=1)

    # Content
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    conversation_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Client info for PRD
    client_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    client_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Service and expert info
    recommended_service: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    matched_expert_id: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType, ForeignKey("experts.id"), nullable=True
    )

    # Storage
    storage_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Analytics
    download_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=default_expiry
    )

    # Relationships
    expert = relationship("Expert", back_populates="prd_documents")

    def __repr__(self) -> str:
        return f"<PRDDocument(id={self.id}, version={self.version})>"

    @property
    def matched_expert(self) -> str | None:
        """Get the name of the matched expert."""
        return self.expert.name if self.expert else None

    @property
    def is_expired(self) -> bool:
        """Check if PRD has expired."""
        return datetime.utcnow() > self.expires_at

    def increment_download(self) -> None:
        """Increment download count."""
        self.download_count += 1
