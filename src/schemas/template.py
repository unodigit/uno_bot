"""Pydantic schemas for welcome message templates."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WelcomeMessageTemplateBase(BaseModel):
    """Base schema for welcome message template."""

    name: str
    content: str
    description: Optional[str] = None
    target_industry: Optional[str] = None
    is_default: bool = False
    is_active: bool = True
    config: dict = {}


class WelcomeMessageTemplateCreate(WelcomeMessageTemplateBase):
    """Schema for creating a new welcome message template."""

    pass


class WelcomeMessageTemplateUpdate(BaseModel):
    """Schema for updating a welcome message template."""

    name: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    target_industry: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    config: Optional[dict] = None


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

    industry: Optional[str] = None
    context: Optional[dict] = None
