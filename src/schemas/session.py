"""Session and message schemas for API validation."""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ClientInfo(BaseModel):
    """Client information collected during conversation."""

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    phone: Optional[str] = None


class BusinessContext(BaseModel):
    """Business context collected during discovery."""

    industry: Optional[str] = None
    challenges: Optional[str] = None
    current_stack: Optional[list[str]] = None
    goals: Optional[str] = None


class Qualification(BaseModel):
    """Qualification data for lead scoring."""

    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    urgency: Optional[str] = None
    decision_maker: Optional[bool] = None
    success_criteria: Optional[str] = None


class SessionCreate(BaseModel):
    """Request schema for creating a new session."""

    visitor_id: str = Field(..., description="Unique visitor identifier")
    source_url: Optional[str] = Field(None, description="URL where chat was started")
    user_agent: Optional[str] = Field(None, description="Browser user agent")


class SessionResponse(BaseModel):
    """Response schema for session data."""

    id: UUID
    visitor_id: str
    status: str
    current_phase: str
    client_info: dict[str, Any]
    business_context: dict[str, Any]
    qualification: dict[str, Any]
    lead_score: Optional[int] = None
    recommended_service: Optional[str] = None
    matched_expert_id: Optional[UUID] = None
    prd_id: Optional[UUID] = None
    booking_id: Optional[UUID] = None
    started_at: datetime
    last_activity: datetime
    completed_at: Optional[datetime] = None
    messages: list["MessageResponse"] = []

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Request schema for sending a message."""

    content: str = Field(..., min_length=1, max_length=10000)
    metadata: Optional[dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Response schema for message data."""

    id: UUID
    session_id: UUID
    role: str
    content: str
    metadata: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class SessionResumeRequest(BaseModel):
    """Request schema for resuming a session."""

    session_id: UUID


# Update forward reference
SessionResponse.model_rebuild()
