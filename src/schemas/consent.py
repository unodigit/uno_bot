"""Consent schemas for GDPR compliance."""

from pydantic import BaseModel, Field


class ConsentCreate(BaseModel):
    """Create consent request schema."""
    visitor_id: str = Field(..., description="Visitor UUID")
    accepted: bool = Field(..., description="Whether consent was accepted")
    declined: bool = Field(..., description="Whether consent was declined")
    timestamp: str = Field(..., description="ISO format timestamp")
    version: str = Field("1.0", description="Consent version")
    data_collected: str | None = Field(None, description="Description of data collected")
    legal_basis: str | None = Field(None, description="Legal basis for data processing")
    retention_period: str | None = Field(None, description="Data retention period")


class ConsentResponse(BaseModel):
    """Consent response schema."""
    id: str
    visitor_id: str
    accepted: bool
    declined: bool
    timestamp: str
    version: str
    data_collected: str | None = None
    legal_basis: str | None = None
    retention_period: str | None = None
    created_at: str

    class Config:
        from_attributes = True
