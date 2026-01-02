"""PRD (Project Requirements Document) API routes."""
import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.prd import PRDDocument
from src.schemas.prd import (
    ConversationSummaryApproveRequest,
    ConversationSummaryResponse,
    PRDCreate,
    PRDPreview,
    PRDRegenerateRequest,
    PRDResponse,
)
from src.services.prd_service import PRDService
from src.services.session_service import SessionService

router = APIRouter()


@router.post(
    "/generate",
    response_model=PRDResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate PRD for session",
    description="Generate a Project Requirements Document for a conversation session",
)
async def generate_prd(
    request: PRDCreate,
    db: AsyncSession = Depends(get_db),
) -> PRDResponse:
    """Generate a PRD for a session.

    This endpoint triggers PRD generation based on the conversation data
    collected during the session. It requires that the session has completed
    the discovery and qualification phases.
    """
    session_service = SessionService(db)
    prd_service = PRDService(db)

    # Get the session
    session = await session_service.get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found",
        )

    # Check if we have enough data
    if not session.client_info.get("name"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client name is required for PRD generation",
        )

    if not session.business_context.get("challenges"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business challenges are required for PRD generation",
        )

    # Generate PRD
    prd = await prd_service.generate_prd(session)

    return PRDResponse(
        id=prd.id,
        session_id=prd.session_id,
        version=prd.version,
        content_markdown=prd.content_markdown,
        conversation_summary=prd.conversation_summary,
        client_company=prd.client_company,
        client_name=prd.client_name,
        recommended_service=prd.recommended_service,
        matched_expert=prd.matched_expert,
        storage_url=prd.storage_url,
        download_count=prd.download_count,
        created_at=prd.created_at,
        expires_at=prd.expires_at,
    )


@router.get(
    "/{prd_id}",
    response_model=PRDResponse,
    summary="Get PRD by ID",
    description="Retrieve a PRD document by its ID",
)
async def get_prd(
    prd_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PRDResponse:
    """Get a PRD document by ID."""
    prd_service = PRDService(db)
    prd = await prd_service.get_prd(prd_id)

    if not prd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PRD {prd_id} not found",
        )

    return PRDResponse(
        id=prd.id,
        session_id=prd.session_id,
        version=prd.version,
        content_markdown=prd.content_markdown,
        conversation_summary=prd.conversation_summary,
        client_company=prd.client_company,
        client_name=prd.client_name,
        recommended_service=prd.recommended_service,
        matched_expert=prd.matched_expert,
        storage_url=prd.storage_url,
        download_count=prd.download_count,
        created_at=prd.created_at,
        expires_at=prd.expires_at,
    )


@router.get(
    "/session/{session_id}",
    response_model=PRDResponse,
    summary="Get PRD by session ID",
    description="Retrieve a PRD document by session ID",
)
async def get_prd_by_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PRDResponse:
    """Get a PRD document by session ID."""
    prd_service = PRDService(db)
    prd = await prd_service.get_prd_by_session(session_id)

    if not prd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No PRD found for session {session_id}",
        )

    return PRDResponse(
        id=prd.id,
        session_id=prd.session_id,
        version=prd.version,
        content_markdown=prd.content_markdown,
        conversation_summary=prd.conversation_summary,
        client_company=prd.client_company,
        client_name=prd.client_name,
        recommended_service=prd.recommended_service,
        matched_expert=prd.matched_expert,
        storage_url=prd.storage_url,
        download_count=prd.download_count,
        created_at=prd.created_at,
        expires_at=prd.expires_at,
    )


@router.get(
    "/{prd_id}/preview",
    response_model=PRDPreview,
    summary="Get PRD preview",
    description="Get a preview of the PRD for chat display",
)
async def get_prd_preview(
    prd_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PRDPreview:
    """Get a PRD preview for chat display."""
    prd_service = PRDService(db)
    prd = await prd_service.get_prd(prd_id)

    if not prd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PRD {prd_id} not found",
        )

    filename = prd_service.generate_filename(prd)
    # Truncate to 197 chars + "..." to meet max_length=200 validation
    preview_text = prd.content_markdown[:197] + "..." if len(prd.content_markdown) > 197 else prd.content_markdown

    return PRDPreview(
        id=prd.id,
        filename=filename,
        preview_text=preview_text,
        version=prd.version,
        created_at=prd.created_at,
    )


@router.get(
    "/{prd_id}/download",
    summary="Download PRD",
    description="Download PRD as a Markdown file",
)
async def download_prd(
    prd_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Download PRD as a Markdown file."""
    prd_service = PRDService(db)
    prd = await prd_service.get_prd(prd_id)

    if not prd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PRD {prd_id} not found",
        )

    # Increment download count
    await prd_service.increment_download_count(prd)

    # Generate filename
    filename = prd_service.generate_filename(prd)

    # Create file content
    content = prd.content_markdown.encode("utf-8")
    file_like = BytesIO(content)

    # Return as streaming response
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "text/markdown; charset=utf-8",
    }

    return StreamingResponse(
        file_like,
        media_type="text/markdown",
        headers=headers,
    )


@router.post(
    "/{prd_id}/regenerate",
    response_model=PRDResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Regenerate PRD",
    description="Regenerate a PRD with optional feedback",
)
async def regenerate_prd(
    prd_id: uuid.UUID,
    request: PRDRegenerateRequest,
    db: AsyncSession = Depends(get_db),
) -> PRDResponse:
    """Regenerate a PRD with optional feedback."""
    prd_service = PRDService(db)
    session_service = SessionService(db)

    # Get existing PRD
    prd = await prd_service.get_prd(prd_id)
    if not prd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PRD {prd_id} not found",
        )

    # Get session
    session = await session_service.get_session(prd.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {prd.session_id} not found",
        )

    # Regenerate PRD
    new_prd = await prd_service.regenerate_prd(session, request.feedback)

    return PRDResponse(
        id=new_prd.id,
        session_id=new_prd.session_id,
        version=new_prd.version,
        content_markdown=new_prd.content_markdown,
        conversation_summary=new_prd.conversation_summary,
        client_company=new_prd.client_company,
        client_name=new_prd.client_name,
        recommended_service=new_prd.recommended_service,
        matched_expert=new_prd.matched_expert,
        storage_url=new_prd.storage_url,
        download_count=new_prd.download_count,
        created_at=new_prd.created_at,
        expires_at=new_prd.expires_at,
    )


@router.post(
    "/generate-summary",
    response_model=ConversationSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate conversation summary",
    description="Generate a summary of the conversation before PRD generation",
)
async def generate_conversation_summary(
    request: PRDCreate,
    db: AsyncSession = Depends(get_db),
) -> ConversationSummaryResponse:
    """Generate a conversation summary for review before PRD generation.

    This endpoint generates a summary of the conversation that the user can
    review and approve before proceeding with PRD generation.
    """
    session_service = SessionService(db)
    prd_service = PRDService(db)

    # Get the session
    session = await session_service.get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found",
        )

    # Check if we have enough data
    if not session.client_info.get("name"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client name is required for summary generation",
        )

    if not session.business_context.get("challenges"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business challenges are required for summary generation",
        )

    # Generate summary
    summary = await prd_service.generate_conversation_summary(session)

    return ConversationSummaryResponse(
        summary=summary,
        session_id=session.id,
    )


@router.post(
    "/approve-summary-and-generate-prd",
    response_model=PRDResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Approve summary and generate PRD",
    description="Approve conversation summary and generate PRD",
)
async def approve_summary_and_generate_prd(
    request: ConversationSummaryApproveRequest,
    db: AsyncSession = Depends(get_db),
) -> PRDResponse:
    """Approve conversation summary and generate PRD.

    If approve is True, generates PRD with the provided summary.
    If approve is False, regenerates a new summary for review.
    """
    session_service = SessionService(db)
    prd_service = PRDService(db)

    # Get the session
    session = await session_service.get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found",
        )

    if not request.approve:
        # Regenerate summary
        summary = await prd_service.generate_conversation_summary(session)
        return ConversationSummaryResponse(
            summary=summary,
            session_id=session.id,
        )

    # Generate PRD with approved summary
    prd = await prd_service.generate_prd(session, request.summary)

    return PRDResponse(
        id=prd.id,
        session_id=prd.session_id,
        version=prd.version,
        content_markdown=prd.content_markdown,
        conversation_summary=prd.conversation_summary,
        client_company=prd.client_company,
        client_name=prd.client_name,
        recommended_service=prd.recommended_service,
        matched_expert=prd.matched_expert,
        storage_url=prd.storage_url,
        download_count=prd.download_count,
        created_at=prd.created_at,
        expires_at=prd.expires_at,
    )
