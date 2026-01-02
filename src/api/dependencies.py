"""FastAPI dependencies for API routes."""
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db


async def get_session_id(x_session_id: Annotated[str | None, Header()] = None) -> str | None:
    """Extract session ID from request header."""
    return x_session_id


async def require_session_id(
    session_id: Annotated[str | None, Depends(get_session_id)]
) -> str:
    """Require session ID to be present."""
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session ID is required",
        )
    return session_id


# Type aliases for dependency injection
DBSession = Annotated[AsyncSession, Depends(get_db)]
SessionId = Annotated[str, Depends(require_session_id)]
OptionalSessionId = Annotated[str | None, Depends(get_session_id)]
