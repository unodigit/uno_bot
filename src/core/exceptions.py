"""Custom exception classes for the UnoBot API."""
from http import HTTPStatus
from typing import Any


class UnoBotError(Exception):
    """Base exception class for UnoBot API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: list[Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or []
        super().__init__(self.message)


class ValidationError(UnoBotError):
    """Validation error for input data."""

    def __init__(self, message: str, field_errors: list[Any] | None = None):
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=field_errors,
        )


class NotFoundError(UnoBotError):
    """Resource not found error."""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with ID {resource_id} not found"
        super().__init__(
            message=message,
            status_code=HTTPStatus.NOT_FOUND,
            error_code="NOT_FOUND",
        )


class BadRequestError(UnoBotError):
    """Bad request error."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_code="BAD_REQUEST",
        )


class ConflictError(UnoBotError):
    """Conflict error (e.g., resource already exists)."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=HTTPStatus.CONFLICT,
            error_code="CONFLICT",
        )


class DatabaseError(UnoBotError):
    """Database operation error."""

    def __init__(self, operation: str, details: str | None = None):
        message = f"Database operation '{operation}' failed"
        if details:
            message += f": {details}"
        super().__init__(
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
        )


class ExternalServiceError(UnoBotError):
    """External service (Google Calendar, SendGrid) error."""

    def __init__(self, service: str, operation: str, details: str | None = None):
        message = f"External service '{service}' operation '{operation}' failed"
        if details:
            message += f": {details}"
        super().__init__(
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code="EXTERNAL_SERVICE_ERROR",
        )
