"""Expert schemas for API validation."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AvailabilityConfig(BaseModel):
    """Expert availability configuration."""

    business_hours_start: str = "09:00"
    business_hours_end: str = "17:00"
    timezone: str = "America/New_York"
    buffer_minutes: int = 15
    slot_duration_minutes: int = 30
    working_days: list[int] = [0, 1, 2, 3, 4]  # Monday-Friday


class ExpertBase(BaseModel):
    """Base expert schema."""

    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    role: str = Field(..., min_length=1, max_length=255)
    bio: str | None = None
    photo_url: str | None = None
    specialties: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)


class ExpertCreate(ExpertBase):
    """Request schema for creating an expert."""

    calendar_id: str | None = None
    availability: dict[str, Any] | None = None
    is_active: bool | None = True


class ExpertUpdate(BaseModel):
    """Request schema for updating an expert."""

    name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    role: str | None = Field(None, min_length=1, max_length=255)
    bio: str | None = None
    photo_url: str | None = None
    specialties: list[str] | None = None
    services: list[str] | None = None
    calendar_id: str | None = None
    availability: dict[str, Any] | None = None
    is_active: bool | None = None
    refresh_token: str | None = None


class ExpertResponse(ExpertBase):
    """Response schema for expert data."""

    id: UUID
    calendar_id: str | None = None
    availability: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        # Exclude refresh_token from serialization for security
        # It's stored encrypted in the database but never returned via API
    )


class ExpertPublicResponse(BaseModel):
    """Public response schema for expert (no sensitive data)."""

    id: UUID
    name: str
    email: str
    role: str
    bio: str | None = None
    photo_url: str | None = None
    specialties: list[str]
    services: list[str]
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class ExpertMatchRequest(BaseModel):
    """Request schema for expert matching."""

    service_type: str | None = None
    specialties: list[str] | None = None


class ExpertMatchResponse(BaseModel):
    """Response schema for expert matching."""

    experts: list[ExpertPublicResponse]
    match_scores: list[float]


class GoogleOAuthRequest(BaseModel):
    """Request schema for Google OAuth flow."""

    expert_id: UUID


class GoogleOAuthCallbackRequest(BaseModel):
    """Request schema for Google OAuth callback."""

    code: str
    state: str | None = None


class GoogleOAuthResponse(BaseModel):
    """Response schema for Google OAuth operations."""

    success: bool
    calendar_id: str | None = None
    message: str | None = None
