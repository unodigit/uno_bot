"""PRD (Project Requirements Document) schemas for API validation."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PRDSection(BaseModel):
    """PRD section structure."""

    title: str
    content: str


class PRDCreate(BaseModel):
    """Request schema for generating a PRD."""

    session_id: UUID


class PRDResponse(BaseModel):
    """Response schema for PRD data."""

    id: UUID
    session_id: UUID
    version: int
    content_markdown: str
    conversation_summary: str | None = None
    client_company: str | None = None
    client_name: str | None = None
    recommended_service: str | None = None
    matched_expert: str | None = None
    storage_url: str | None = None
    download_count: int
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class PRDPreview(BaseModel):
    """Preview schema for PRD in chat."""

    id: UUID
    filename: str
    preview_text: str = Field(..., max_length=200)
    version: int
    created_at: datetime


class PRDDownloadResponse(BaseModel):
    """Response schema for PRD download."""

    id: UUID
    filename: str
    content_type: str = "text/markdown"
    download_url: str


class PRDRegenerateRequest(BaseModel):
    """Request schema for regenerating a PRD."""

    session_id: UUID
    feedback: str | None = Field(None, description="Optional feedback for regeneration")


class ConversationSummaryResponse(BaseModel):
    """Response schema for conversation summary."""

    summary: str
    session_id: UUID


class ConversationSummaryApproveRequest(BaseModel):
    """Request schema for approving conversation summary."""

    session_id: UUID
    summary: str
    approve: bool = Field(..., description="True to approve, False to regenerate")
