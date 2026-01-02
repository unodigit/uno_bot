"""Expert API routes for CRUD operations."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.expert import (
    ExpertCreate,
    ExpertMatchRequest,
    ExpertMatchResponse,
    ExpertPublicResponse,
    ExpertResponse,
    ExpertUpdate,
)
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
    expert = await service.get_expert(expert_id)

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
    expert = await service.get_expert(expert_id)

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
            role=expert.role,
            bio=expert.bio,
            photo_url=expert.photo_url,
            specialties=expert.specialties,
            services=expert.services,
        ))
        match_scores.append(score)

    return ExpertMatchResponse(
        experts=experts,
        match_scores=match_scores,
    )
