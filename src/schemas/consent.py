"""Consent schemas for GDPR compliance."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConsentCreate(BaseModel):
    """Create consent request schema."""
    visitor_id: str = Field(..., description="Visitor UUID")
    accepted: bool = Field(..., description="Whether consent was accepted")
    declined: bool = Field(..., description="Whether consent was declined")
    timestamp: str = Field(..., description="ISO format timestamp")
    version: str = Field("1.0", description="Consent version")
    data_collected: Optional[str] = Field(None, description="Description of data collected")
    legal_basis: Optional[str] = Field(None, description="Legal basis for data processing")
    retention_period: Optional[str] = Field(None, description="Data retention period")


class ConsentResponse(BaseModel):
    """Consent response schema."""
    id: str
    visitor_id: str
    accepted: bool
    declined: bool
    timestamp: str
    version: str
    data_collected: Optional[str] = None
    legal_basis: Optional[str] = None
    retention_period: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True