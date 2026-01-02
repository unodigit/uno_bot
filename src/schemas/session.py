"""Session and message schemas for API validation."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ClientInfo(BaseModel):
    """Client information collected during conversation."""

    name: str | None = None
    email: EmailStr | None = None
    company: str | None = None
    phone: str | None = None


class BusinessContext(BaseModel):
    """Business context collected during discovery."""

    industry: str | None = None
    challenges: str | None = None
    current_stack: list[str] | None = None
    goals: str | None = None


class Qualification(BaseModel):
    """Qualification data for lead scoring."""

    budget_range: str | None = None
    timeline: str | None = None
    urgency: str | None = None
    decision_maker: bool | None = None
    success_criteria: str | None = None


class SessionCreate(BaseModel):
    """Request schema for creating a new session."""

    visitor_id: str = Field(..., description="Unique visitor identifier")
    source_url: str | None = Field(None, description="URL where chat was started")
    user_agent: str | None = Field(None, description="Browser user agent")


class SessionResponse(BaseModel):
    """Response schema for session data."""

    id: UUID
    visitor_id: str
    status: str
    current_phase: str
    client_info: dict[str, Any]
    business_context: dict[str, Any]
    qualification: dict[str, Any]
    lead_score: int | None = None
    recommended_service: str | None = None
    matched_expert_id: UUID | None = None
    prd_id: UUID | None = None
    booking_id: UUID | None = None
    started_at: datetime
    last_activity: datetime
    completed_at: datetime | None = None
    messages: list["MessageResponse"] = []

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Request schema for sending a message."""

    content: str = Field(..., min_length=1, max_length=10000)
    metadata: dict[str, Any] | None = Field(None, alias="meta_data")


class MessageResponse(BaseModel):
    """Response schema for message data."""

    id: UUID
    session_id: UUID
    role: str
    content: str
    meta_data: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class SessionResumeRequest(BaseModel):
    """Request schema for resuming a session."""

    session_id: UUID


# Update forward reference
SessionResponse.model_rebuild()
