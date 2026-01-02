"""Session and message API routes."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.session import MessageRole
from src.schemas.session import (
    MessageCreate,
    MessageResponse,
    SessionCreate,
    SessionResponse,
    SessionResumeRequest,
)
from src.services.session_service import SessionService

router = APIRouter()


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new chat session",
    description="Create a new conversation session for a visitor",
)
async def create_session(
    session_create: SessionCreate,
    db: AsyncSession = Depends(get_db),
) -> SessionResponse:
    """Create a new chat session.

    This endpoint initializes a new conversation session for a visitor.
    It creates the session with an initial welcome message and returns
    the session details including the session ID for subsequent requests.
    """
    service = SessionService(db)
    session = await service.create_session(session_create)

    # Convert to response model with messages
    return SessionResponse(
        id=session.id,
        visitor_id=session.visitor_id,
        status=session.status,
        current_phase=session.current_phase,
        client_info=session.client_info,
        business_context=session.business_context,
        qualification=session.qualification,
        lead_score=session.lead_score,
        recommended_service=session.recommended_service,
        matched_expert_id=session.matched_expert_id,
        prd_id=session.prd_id,
        booking_id=session.booking_id,
        started_at=session.started_at,
        last_activity=session.last_activity,
        completed_at=session.completed_at,
        messages=[
            MessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                role=msg.role,
                content=msg.content,
                metadata=msg.metadata,
                created_at=msg.created_at,
            )
            for msg in session.messages
        ],
    )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Get session by ID",
    description="Retrieve a session and its message history",
)
async def get_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> SessionResponse:
    """Get session details and message history.

    Retrieve a conversation session by its ID, including all messages
    and session metadata.
    """
    service = SessionService(db)
    session = await service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    return SessionResponse(
        id=session.id,
        visitor_id=session.visitor_id,
        status=session.status,
        current_phase=session.current_phase,
        client_info=session.client_info,
        business_context=session.business_context,
        qualification=session.qualification,
        lead_score=session.lead_score,
        recommended_service=session.recommended_service,
        matched_expert_id=session.matched_expert_id,
        prd_id=session.prd_id,
        booking_id=session.booking_id,
        started_at=session.started_at,
        last_activity=session.last_activity,
        completed_at=session.completed_at,
        messages=[
            MessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                role=msg.role,
                content=msg.content,
                metadata=msg.metadata,
                created_at=msg.created_at,
            )
            for msg in session.messages
        ],
    )


@router.post(
    "/{session_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send message to session",
    description="Send a user message to the session",
)
async def send_message(
    session_id: uuid.UUID,
    message_create: MessageCreate,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Send a message to a session.

    Add a user message to the conversation session and update
    the session's last activity timestamp.
    """
    service = SessionService(db)
    session = await service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot send message to {session.status} session",
        )

    # Add user message
    message = await service.add_message(
        session_id, message_create, MessageRole.USER
    )

    # Update session activity
    await service.update_session_activity(session)

    return MessageResponse(
        id=message.id,
        session_id=message.session_id,
        role=message.role,
        content=message.content,
        metadata=message.metadata,
        created_at=message.created_at,
    )


@router.post(
    "/{session_id}/resume",
    response_model=SessionResponse,
    summary="Resume session",
    description="Resume an existing session",
)
async def resume_session(
    session_id: uuid.UUID,
    resume_request: SessionResumeRequest,
    db: AsyncSession = Depends(get_db),
) -> SessionResponse:
    """Resume an existing session.

    Mark a session as active again and update its last activity timestamp.
    This allows visitors to continue conversations after leaving the page.
    """
    service = SessionService(db)
    session = await service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot resume a completed session",
        )

    resumed_session = await service.resume_session(session)

    return SessionResponse(
        id=resumed_session.id,
        visitor_id=resumed_session.visitor_id,
        status=resumed_session.status,
        current_phase=resumed_session.current_phase,
        client_info=resumed_session.client_info,
        business_context=resumed_session.business_context,
        qualification=resumed_session.qualification,
        lead_score=resumed_session.lead_score,
        recommended_service=resumed_session.recommended_service,
        matched_expert_id=resumed_session.matched_expert_id,
        prd_id=resumed_session.prd_id,
        booking_id=resumed_session.booking_id,
        started_at=resumed_session.started_at,
        last_activity=resumed_session.last_activity,
        completed_at=resumed_session.completed_at,
        messages=[
            MessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                role=msg.role,
                content=msg.content,
                metadata=msg.metadata,
                created_at=msg.created_at,
            )
            for msg in resumed_session.messages
        ],
    )
