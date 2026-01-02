"""Pydantic schemas for welcome message templates."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WelcomeMessageTemplateBase(BaseModel):
    """Base schema for welcome message template."""

    name: str
    content: str
    description: str | None = None
    target_industry: str | None = None
    is_default: bool = False
    is_active: bool = True
    config: dict[str, Any] = {}


class WelcomeMessageTemplateCreate(WelcomeMessageTemplateBase):
    """Schema for creating a new welcome message template."""

    pass


class WelcomeMessageTemplateUpdate(BaseModel):
    """Schema for updating a welcome message template."""

    name: str | None = None
    content: str | None = None
    description: str | None = None
    target_industry: str | None = None
    is_default: bool | None = None
    is_active: bool | None = None
    config: dict[str, Any] | None = None


class WelcomeMessageTemplateResponse(WelcomeMessageTemplateBase):
    """Schema for welcome message template response."""

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )

    id: UUID
    use_count: int
    created_at: datetime
    updated_at: datetime


class WelcomeMessageSelectionRequest(BaseModel):
    """Schema for selecting a welcome message template for a session."""

    industry: str | None = None
    context: dict[str, Any] | None = None
