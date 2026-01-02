"""Session and message API routes."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.session import MessageRole
from src.schemas.expert import ExpertMatchResponse
from src.schemas.session import (
    MessageCreate,
    MessageResponse,
    SessionCreate,
    SessionResponse,
    SessionResumeRequest,
    SessionUpdateRequest,
)
from src.services.expert_service import ExpertService
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
        source_url=session.source_url,
        user_agent=session.user_agent,
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
                meta_data=msg.meta_data,
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
        source_url=session.source_url,
        user_agent=session.user_agent,
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
                meta_data=msg.meta_data,
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

    Add a user message to the conversation session and return the user message.
    The AI response will be sent via WebSocket for real-time streaming.
    """
    service = SessionService(db)
    session = await service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Check if session is active (handle both string and enum)
    status_value = session.status.value if hasattr(session.status, 'value') else session.status
    if status_value != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot send message to {status_value} session",
        )

    # Add user message
    user_message = await service.add_message(
        session_id, message_create, MessageRole.USER
    )

    # Update session activity
    await service.update_session_activity(session)

    # Generate AI response (will be sent via WebSocket in production)
    # For now, we generate it but return the user message
    await service.generate_ai_response(session, message_create.content)

    return MessageResponse(
        id=user_message.id,
        session_id=user_message.session_id,
        role=user_message.role,
        content=user_message.content,
        meta_data=user_message.meta_data,
        created_at=user_message.created_at,
    )


@router.post(
    "/{session_id}/resume",
    response_model=SessionResponse,
    summary="Resume session (path-based)",
    description="Resume an existing session using session_id in URL path",
)
async def resume_session_path(
    session_id: uuid.UUID,
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

    # Check if session is completed (handle both string and enum)
    status_value = session.status.value if hasattr(session.status, 'value') else session.status
    if status_value == "completed":
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
        source_url=resumed_session.source_url,
        user_agent=resumed_session.user_agent,
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
                meta_data=msg.meta_data,
                created_at=msg.created_at,
            )
            for msg in resumed_session.messages
        ],
    )


@router.post(
    "/resume",
    response_model=SessionResponse,
    summary="Resume session",
    description="Resume an existing session using session_id in request body",
)
async def resume_session(
    resume_request: SessionResumeRequest,
    db: AsyncSession = Depends(get_db),
) -> SessionResponse:
    """Resume an existing session.

    Mark a session as active again and update its last activity timestamp.
    This allows visitors to continue conversations after leaving the page.
    Uses session_id from request body.
    """
    if not resume_request.session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id is required in request body",
        )

    service = SessionService(db)
    session = await service.get_session(resume_request.session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {resume_request.session_id} not found",
        )

    # Check if session is completed (handle both string and enum)
    status_value = session.status.value if hasattr(session.status, 'value') else session.status
    if status_value == "completed":
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
        source_url=resumed_session.source_url,
        user_agent=resumed_session.user_agent,
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
                meta_data=msg.meta_data,
                created_at=msg.created_at,
            )
            for msg in resumed_session.messages
        ],
    )


@router.post(
    "/{session_id}/match-expert",
    response_model=ExpertMatchResponse,
    summary="Match experts to session",
    description="Find matching experts based on session context and service needs",
)
async def match_expert(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ExpertMatchResponse:
    """Match experts to a session based on qualification data.

    Analyzes the session's business context, recommended service, and
    qualification data to find the most relevant experts. Returns
    ranked experts with match scores.
    """
    session_service = SessionService(db)
    session = await session_service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    expert_service = ExpertService(db)

    # Get matching experts with scores
    scored_experts = await expert_service.match_experts(
        service_type=session.recommended_service,
        business_context=session.business_context,
    )

    # Extract experts and scores for response
    from src.schemas.expert import ExpertPublicResponse

    experts = []
    scores = []

    for expert, score in scored_experts:
        experts.append(
            ExpertPublicResponse(
                id=expert.id,
                name=expert.name,
                email=expert.email,
                role=expert.role,
                bio=expert.bio,
                photo_url=expert.photo_url,
                specialties=expert.specialties,
                services=expert.services,
                is_active=expert.is_active,
            )
        )
        scores.append(score)

    # Auto-select top expert if available
    if scored_experts:
        top_expert = scored_experts[0][0]
        # Update session with matched expert (using client_info to store it temporarily)
        # Note: matched_expert_id is a direct column, so we need to update it differently
        session.matched_expert_id = top_expert.id
        db.add(session)
        await db.commit()
        await db.refresh(session)

    return ExpertMatchResponse(
        experts=experts,
        match_scores=scores,
    )


@router.patch(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Update session data",
    description="Update session metadata (business context, qualification, etc.)",
)
async def update_session(
    session_id: uuid.UUID,
    updates: SessionUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> SessionResponse:
    """Update session metadata.

    Allows partial updates to session fields like business_context,
    qualification, recommended_service, etc.
    """
    service = SessionService(db)
    session = await service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Update session with provided data using keyword arguments
    updated_session = await service.update_session_data(
        session,
        client_info=updates.client_info,
        business_context=updates.business_context,
        qualification=updates.qualification,
        lead_score=updates.lead_score,
        recommended_service=updates.recommended_service,
    )

    return SessionResponse(
        id=updated_session.id,
        visitor_id=updated_session.visitor_id,
        status=updated_session.status,
        current_phase=updated_session.current_phase,
        source_url=updated_session.source_url,
        user_agent=updated_session.user_agent,
        client_info=updated_session.client_info,
        business_context=updated_session.business_context,
        qualification=updated_session.qualification,
        lead_score=updated_session.lead_score,
        recommended_service=updated_session.recommended_service,
        matched_expert_id=updated_session.matched_expert_id,
        prd_id=updated_session.prd_id,
        booking_id=updated_session.booking_id,
        started_at=updated_session.started_at,
        last_activity=updated_session.last_activity,
        completed_at=updated_session.completed_at,
        messages=[
            MessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                role=msg.role,
                content=msg.content,
                meta_data=msg.meta_data,
                created_at=msg.created_at,
            )
            for msg in updated_session.messages
        ],
    )
