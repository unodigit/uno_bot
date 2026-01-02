"""Expert API routes for CRUD operations."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.booking import AvailabilityResponse
from src.schemas.expert import (
    ExpertCreate,
    ExpertMatchRequest,
    ExpertMatchResponse,
    ExpertPublicResponse,
    ExpertResponse,
    ExpertUpdate,
    GoogleOAuthResponse,
)
from src.services.booking_service import BookingService
from src.services.calendar_service import CalendarService
from src.services.expert_service import ExpertService

router = APIRouter()


@router.get(
    "",
    response_model=list[ExpertPublicResponse],
    summary="List all active experts",
    description="Get a list of all active expert profiles",
)
async def list_experts(
    db: AsyncSession = Depends(get_db),
) -> list[ExpertPublicResponse]:
    """List all active experts.

    Returns a list of public expert profiles that are currently active.
    Sensitive information like refresh tokens is excluded.
    """
    service = ExpertService(db)
    experts = await service.list_active_experts()

    return [
        ExpertPublicResponse(
            id=expert.id,
            name=expert.name,
            email=expert.email,
            photo_url=expert.photo_url,
            role=expert.role,
            bio=expert.bio,
            specialties=expert.specialties,
            services=expert.services,
            is_active=expert.is_active,
        )
        for expert in experts
    ]


@router.get(
    "/{expert_id}",
    response_model=ExpertPublicResponse,
    summary="Get expert by ID",
    description="Get a public expert profile by ID",
)
async def get_expert(
    expert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ExpertPublicResponse:
    """Get an expert profile by ID.

    Returns public information about an expert. Sensitive information
    like refresh tokens is excluded.
    """
    service = ExpertService(db)
    expert = await service.get_expert(expert_id)

    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expert {expert_id} not found",
        )

    return ExpertPublicResponse(
        id=expert.id,
        name=expert.name,
        email=expert.email,
        photo_url=expert.photo_url,
        role=expert.role,
        bio=expert.bio,
        specialties=expert.specialties,
        services=expert.services,
        is_active=expert.is_active,
    )


@router.get(
    "/{expert_id}/availability",
    response_model=AvailabilityResponse,
    summary="Get expert availability",
    description="Get available time slots for an expert",
)
async def get_expert_availability(
    expert_id: uuid.UUID,
    timezone: str | None = None,
    days_ahead: int | None = None,
    min_slots_to_show: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> AvailabilityResponse:
    """Get available time slots for an expert.

    Args:
        expert_id: Expert UUID
        timezone: Timezone for availability (defaults to expert's calendar timezone)
        days_ahead: Number of days to look ahead for availability
        min_slots_to_show: Minimum number of slots to return
        db: Database session

    Returns:
        AvailabilityResponse with grouped time slots
    """
    booking_service = BookingService(db)

    try:
        availability = await booking_service.get_expert_availability(
            expert_id=expert_id,
            timezone=timezone,
            days_ahead=days_ahead,
            min_slots_to_show=min_slots_to_show
        )
        return availability
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get availability: {str(e)}"
        ) from e


@router.post(
    "",
    response_model=ExpertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new expert",
    description="Create a new expert profile (admin only)",
)
async def create_expert(
    expert_create: ExpertCreate,
    db: AsyncSession = Depends(get_db),
) -> ExpertResponse:
    """Create a new expert profile.

    This endpoint is intended for admin use to create new expert profiles.
    """
    service = ExpertService(db)
    expert = await service.create_expert(expert_create)

    return ExpertResponse(
        id=expert.id,
        name=expert.name,
        email=expert.email,
        calendar_id=expert.calendar_id,
        photo_url=expert.photo_url,
        role=expert.role,
        bio=expert.bio,
        specialties=expert.specialties,
        services=expert.services,
        availability=expert.availability,
        is_active=expert.is_active,
        created_at=expert.created_at,
        updated_at=expert.updated_at,
    )


@router.put(
    "/{expert_id}",
    response_model=ExpertResponse,
    summary="Update expert",
    description="Update an expert profile (admin only)",
)
async def update_expert(
    expert_id: uuid.UUID,
    expert_update: ExpertUpdate,
    db: AsyncSession = Depends(get_db),
) -> ExpertResponse:
    """Update an expert profile.

    This endpoint is intended for admin use to update expert profiles.
    """
    service = ExpertService(db)
    expert = await service.get_expert_model(expert_id)

    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expert {expert_id} not found",
        )

    updated_expert = await service.update_expert(expert, expert_update)

    return ExpertResponse(
        id=updated_expert.id,
        name=updated_expert.name,
        email=updated_expert.email,
        calendar_id=updated_expert.calendar_id,
        photo_url=updated_expert.photo_url,
        role=updated_expert.role,
        bio=updated_expert.bio,
        specialties=updated_expert.specialties,
        services=updated_expert.services,
        availability=updated_expert.availability,
        is_active=updated_expert.is_active,
        created_at=updated_expert.created_at,
        updated_at=updated_expert.updated_at,
    )


@router.delete(
    "/{expert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete expert",
    description="Delete an expert profile (admin only)",
)
async def delete_expert(
    expert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an expert profile.

    This endpoint is intended for admin use to delete expert profiles.
    """
    service = ExpertService(db)
    expert = await service.get_expert_model(expert_id)

    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expert {expert_id} not found",
        )

    await service.delete_expert(expert)


@router.post(
    "/match",
    response_model=ExpertMatchResponse,
    summary="Match experts to requirements",
    description="Find and rank experts based on service type, specialties, and business context",
)
async def match_experts(
    request: ExpertMatchRequest,
    db: AsyncSession = Depends(get_db),
) -> ExpertMatchResponse:
    """Match experts to project requirements.

    Returns a list of experts ranked by relevance to the specified
    service type, specialties, and business context.
    """
    service = ExpertService(db)
    matched_experts = await service.match_experts(
        service_type=request.service_type,
        specialties=request.specialties,
    )

    # Convert to response format
    experts = []
    match_scores = []
    for expert, score in matched_experts:
        experts.append(ExpertPublicResponse(
            id=expert.id,
            name=expert.name,
            email=expert.email,
            photo_url=expert.photo_url,
            role=expert.role,
            bio=expert.bio,
            specialties=expert.specialties,
            services=expert.services,
            is_active=expert.is_active,
        ))
        match_scores.append(score)

    return ExpertMatchResponse(
        experts=experts,
        match_scores=match_scores,
    )


@router.post(
    "/{expert_id}/connect_calendar",
    response_model=GoogleOAuthResponse,
    summary="Initiate Google Calendar OAuth flow",
    description="Start Google Calendar OAuth flow for an expert",
)
async def connect_calendar(
    expert_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> GoogleOAuthResponse:
    """Initiate Google Calendar OAuth flow for an expert.

    Args:
        expert_id: Expert UUID
        request: FastAPI request object
        db: Database session

    Returns:
        OAuth URL for redirecting the user to Google's consent screen
    """
    expert_service = ExpertService(db)
    calendar_service = CalendarService()

    # Verify expert exists
    expert = await expert_service.get_expert(expert_id)
    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expert {expert_id} not found",
        )

    try:
        # Create OAuth flow
        flow = calendar_service.create_oauth_flow()

        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent to get refresh token
        )

        return GoogleOAuthResponse(
            success=True,
            message=authorization_url,
            calendar_id=None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OAuth flow: {str(e)}"
        ) from e


@router.get(
    "/calendar/callback",
    response_model=GoogleOAuthResponse,
    summary="Handle Google OAuth callback",
    description="Handle Google OAuth callback and store credentials",
)
async def oauth_callback(
    request: Request,
    code: str,
    state: str | None = None,
    expert_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> GoogleOAuthResponse:
    """Handle Google OAuth callback and store credentials.

    Args:
        request: FastAPI request object
        code: Authorization code from Google
        state: State parameter from OAuth flow
        expert_id: Expert UUID (can be passed as query param)
        db: Database session

    Returns:
        Success status and calendar ID
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code is required"
        )

    # Check expert_id BEFORE trying to fetch token
    if not expert_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expert ID is required"
        )

    calendar_service = CalendarService()

    try:
        # Create OAuth flow
        flow = calendar_service.create_oauth_flow()

        # Exchange authorization code for credentials
        flow.fetch_token(code=code)

        # Get credentials
        credentials = flow.credentials

        # Store refresh token
        if credentials.refresh_token:
            expert_service = ExpertService(db)
            expert = await expert_service.get_expert_model(expert_id)
            if not expert:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Expert {expert_id} not found",
                )

            # Update expert with refresh token and calendar ID
            await expert_service.update_expert(expert, ExpertUpdate(
                name=None,
                role=None,
                refresh_token=credentials.refresh_token,
                calendar_id=credentials.client_id  # Store client_id as calendar_id for now
            ))

            return GoogleOAuthResponse(
                success=True,
                calendar_id=str(expert_id),  # Return expert_id as calendar_id
                message="Calendar connected successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No refresh token received"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}"
        ) from e
