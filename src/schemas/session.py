"""Session and message schemas for API validation."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
    source_url: str | None = None
    user_agent: str | None = None
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
    email_opt_in: bool = Field(default=False)
    email_preferences: dict[str, Any] = Field(default_factory=dict)
    messages: list["MessageResponse"] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


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

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class SessionResumeRequest(BaseModel):
    """Request schema for resuming a session.

    Accepts session_id in body for body-based resume endpoint.
    For path-based resume, session_id comes from URL path.
    """

    session_id: UUID | None = Field(None, description="Session ID to resume (required for body-based resume)")


class UnsubscribeRequest(BaseModel):
    """Request schema for unsubscribing from marketing emails."""

    session_id: UUID = Field(..., description="Session ID to unsubscribe")


class SessionUpdateRequest(BaseModel):
    """Request schema for updating session data."""

    client_info: dict[str, Any] | None = Field(None, description="Client information to update")
    business_context: dict[str, Any] | None = Field(None, description="Business context to update")
    qualification: dict[str, Any] | None = Field(None, description="Qualification data to update")
    lead_score: int | None = Field(None, description="Lead score to set")
    recommended_service: str | None = Field(None, description="Recommended service to set")


# Update forward reference
SessionResponse.model_rebuild()
