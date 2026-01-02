"""PRD (Project Requirements Document) schemas for API validation."""
from datetime import datetime
from typing import Optional
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
    client_company: Optional[str] = None
    client_name: Optional[str] = None
    recommended_service: Optional[str] = None
    matched_expert: Optional[str] = None
    storage_url: Optional[str] = None
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
    feedback: Optional[str] = Field(None, description="Optional feedback for regeneration")
