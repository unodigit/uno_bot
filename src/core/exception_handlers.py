"""Exception handlers for the UnoBot API."""
import logging
from typing import Any, Dict, List, Union

from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.config import settings
from src.core.exceptions import (
    BadRequestError,
    ConflictError,
    DatabaseError,
    ExternalServiceError,
    NotFoundError,
    UnoBotError,
)
from src.schemas.error import (
    BadRequestError as BadRequestErrorResponse,
    ConflictError as ConflictErrorResponse,
    ErrorResponse,
    InternalServerError,
    NotFoundError as NotFoundErrorResponse,
    ValidationErrorResponse,
)

logger = logging.getLogger(__name__)

# Type alias for all possible error response types
ErrorResponseUnion = Union[
    ValidationErrorResponse,
    BadRequestErrorResponse,
    NotFoundErrorResponse,
    ConflictErrorResponse,
    InternalServerError,
]


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    # Extract field-level errors
    field_errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        field_errors.append(
            {
                "field": field,
                "message": error["msg"],
                "value": error.get("input", None),
            }
        )

    error_response: ValidationErrorResponse = ValidationErrorResponse(
        success=False,
        detail="Validation failed",
        error_code="VALIDATION_ERROR",
        path=str(request.url),
        details=field_errors,
    )

    if settings.debug:
        error_response.debug_info = {
            "validation_errors": exc.errors(),
            "body": exc.body if hasattr(exc, "body") else None,
        }

    return JSONResponse(
        status_code=422,
        content=error_response.model_dump(mode='json', exclude_none=True),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    error_response: ErrorResponseUnion
    if exc.status_code == 404:
        error_response = NotFoundErrorResponse(
            success=False,
            detail=exc.detail,
            error_code="NOT_FOUND",
            path=str(request.url),
        )
    elif exc.status_code == 400:
        error_response = BadRequestErrorResponse(
            success=False,
            detail=exc.detail,
            error_code="BAD_REQUEST",
            path=str(request.url),
        )
    elif exc.status_code == 409:
        error_response = ConflictErrorResponse(
            success=False,
            detail=exc.detail,
            error_code="CONFLICT",
            path=str(request.url),
        )
    else:
        error_response = InternalServerError(
            success=False,
            detail=exc.detail,
            error_code="INTERNAL_ERROR",
            path=str(request.url),
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode='json', exclude_none=True),
    )


async def unobot_exception_handler(request: Request, exc: UnoBotError) -> JSONResponse:
    """Handle custom UnoBot exceptions."""
    error_response: ErrorResponseUnion
    if isinstance(exc, NotFoundError):
        error_response = NotFoundErrorResponse(
            success=False,
            detail=exc.message,
            error_code=exc.error_code,
            path=str(request.url),
        )
    elif isinstance(exc, BadRequestError):
        error_response = BadRequestErrorResponse(
            success=False,
            detail=exc.message,
            error_code=exc.error_code,
            path=str(request.url),
        )
    elif isinstance(exc, ConflictError):
        error_response = ConflictErrorResponse(
            success=False,
            detail=exc.message,
            error_code=exc.error_code,
            path=str(request.url),
        )
    else:
        error_response = InternalServerError(
            success=False,
            detail=exc.message,
            error_code=exc.error_code,
            path=str(request.url),
        )

    if settings.debug:
        error_response.debug_info = {
            "exception_type": exc.__class__.__name__,
            "exception_details": str(exc),
        }

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode='json', exclude_none=True),
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database exceptions."""
    logger.error(f"Database error: {exc}")

    # Check for specific database error types
    error_response: ErrorResponseUnion
    status_code: int
    if isinstance(exc, IntegrityError):
        error_response = ConflictErrorResponse(
            success=False,
            detail="Database constraint violation",
            error_code="INTEGRITY_ERROR",
            path=str(request.url),
        )
        status_code = 409
    else:
        error_response = InternalServerError(
            success=False,
            detail="Database operation failed",
            error_code="DATABASE_ERROR",
            path=str(request.url),
        )
        status_code = 500

    if settings.debug:
        error_response.debug_info = {
            "exception_type": exc.__class__.__name__,
            "exception_details": str(exc),
        }

    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(mode='json', exclude_none=True),
    )


async def external_service_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle external service exceptions (Google Calendar, SendGrid, etc.)."""
    logger.error(f"External service error: {exc}")

    error_response: InternalServerError = InternalServerError(
        success=False,
        detail="External service temporarily unavailable",
        error_code="EXTERNAL_SERVICE_ERROR",
        path=str(request.url),
    )

    if settings.debug:
        error_response.debug_info = {
            "exception_type": exc.__class__.__name__,
            "exception_details": str(exc),
        }

    return JSONResponse(
        status_code=503,
        content=error_response.model_dump(mode='json', exclude_none=True),
    )


def register_exception_handlers(app) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(UnoBotError, unobot_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, external_service_exception_handler)
