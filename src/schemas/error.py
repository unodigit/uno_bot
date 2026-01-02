"""Error response schemas for API validation."""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ValidationErrorDetail(BaseModel):
    """Validation error detail for field-level errors."""

    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Error message for the field")
    value: Any | None = Field(None, description="Value that failed validation")


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    success: bool = Field(False, description="Always false for error responses")
    detail: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Machine-readable error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    path: str | None = Field(None, description="API endpoint path")
    details: list[ValidationErrorDetail] | None = Field(
        default=None, description="Field-level validation errors"
    )
    debug_info: dict[str, Any] | None = Field(
        default=None, description="Additional debug information (development only)"
    )


class BadRequestError(ErrorResponse):
    """400 Bad Request error response."""

    error_code: Literal["BAD_REQUEST"] = "BAD_REQUEST"


class NotFoundError(ErrorResponse):
    """404 Not Found error response."""

    error_code: Literal["NOT_FOUND"] = "NOT_FOUND"


class ValidationErrorResponse(ErrorResponse):
    """422 Validation Error response with field details."""

    error_code: Literal["VALIDATION_ERROR"] = "VALIDATION_ERROR"
    details: list[ValidationErrorDetail] = Field(default_factory=list, description="Field validation errors")


class InternalServerError(ErrorResponse):
    """500 Internal Server Error response."""

    # Note: This uses str instead of Literal to allow custom error codes
    # like "DATABASE_ERROR", "EXTERNAL_SERVICE_ERROR", "INTEGRITY_ERROR"
    error_code: str = Field("INTERNAL_ERROR", description="Machine-readable error code")


class ConflictError(ErrorResponse):
    """409 Conflict error response."""

    error_code: Literal["CONFLICT"] = "CONFLICT"


# Type alias for all error response types that can be used in exception handlers
# This includes InternalServerError which supports custom error codes
AnyErrorResponse = InternalServerError
