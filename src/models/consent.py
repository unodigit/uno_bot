"""Consent model for GDPR compliance."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Consent(Base):
    """Consent record for GDPR compliance."""

    __tablename__ = "consents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    visitor_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    accepted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    declined: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    data_collected: Mapped[str | None] = mapped_column(Text, nullable=True)
    legal_basis: Mapped[str | None] = mapped_column(String(255), nullable=True)
    retention_period: Mapped[str | None] = mapped_column(String(100), nullable=True)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<Consent(id={self.id}, visitor_id={self.visitor_id}, accepted={self.accepted}, timestamp={self.timestamp})>"
