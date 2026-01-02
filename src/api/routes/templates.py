"""Welcome message template API routes."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.template import (
    WelcomeMessageSelectionRequest,
    WelcomeMessageTemplateCreate,
    WelcomeMessageTemplateResponse,
    WelcomeMessageTemplateUpdate,
)
from src.services.template_service import TemplateService

router = APIRouter()


@router.post(
    "",
    response_model=WelcomeMessageTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create welcome message template",
    description="Create a new welcome message template for admin configuration",
)
async def create_template(
    template_create: WelcomeMessageTemplateCreate,
    db: AsyncSession = Depends(get_db),
) -> WelcomeMessageTemplateResponse:
    """Create a new welcome message template.

    This endpoint allows administrators to create customizable welcome messages
    that can be targeted by industry or used as defaults.
    """
    service = TemplateService(db)
    template = await service.create_template(template_create)
    return template


@router.get(
    "",
    response_model=list[WelcomeMessageTemplateResponse],
    summary="List all templates",
    description="Get all welcome message templates",
)
async def list_templates(
    db: AsyncSession = Depends(get_db),
) -> list[WelcomeMessageTemplateResponse]:
    """List all welcome message templates."""
    service = TemplateService(db)
    templates = await service.get_all_templates()
    return templates


@router.get(
    "/active",
    response_model=list[WelcomeMessageTemplateResponse],
    summary="List active templates",
    description="Get all active welcome message templates",
)
async def list_active_templates(
    db: AsyncSession = Depends(get_db),
) -> list[WelcomeMessageTemplateResponse]:
    """List all active welcome message templates."""
    service = TemplateService(db)
    templates = await service.get_active_templates()
    return templates


@router.get(
    "/default",
    response_model=WelcomeMessageTemplateResponse,
    summary="Get default template",
    description="Get the default welcome message template",
)
async def get_default_template(
    db: AsyncSession = Depends(get_db),
) -> WelcomeMessageTemplateResponse:
    """Get the default welcome message template."""
    service = TemplateService(db)
    template = await service.get_default_template()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No default template found",
        )

    return template


@router.get(
    "/{template_id}",
    response_model=WelcomeMessageTemplateResponse,
    summary="Get template by ID",
    description="Get a specific welcome message template by ID",
)
async def get_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> WelcomeMessageTemplateResponse:
    """Get a specific welcome message template by ID."""
    service = TemplateService(db)
    template = await service.get_template(template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )

    return template


@router.post(
    "/select",
    response_model=WelcomeMessageTemplateResponse,
    summary="Select template for session",
    description="Select an appropriate welcome message template based on context",
)
async def select_template(
    selection_request: WelcomeMessageSelectionRequest,
    db: AsyncSession = Depends(get_db),
) -> WelcomeMessageTemplateResponse:
    """Select an appropriate welcome message template.

    This endpoint is used by the session service to get the right welcome
    message based on the user's industry or other context.
    """
    service = TemplateService(db)
    template = await service.get_template_for_industry(selection_request.industry)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No suitable template found",
        )

    # Increment use count
    await service.increment_use_count(template.id)

    return template


@router.patch(
    "/{template_id}",
    response_model=WelcomeMessageTemplateResponse,
    summary="Update template",
    description="Update a welcome message template",
)
async def update_template(
    template_id: uuid.UUID,
    template_update: WelcomeMessageTemplateUpdate,
    db: AsyncSession = Depends(get_db),
) -> WelcomeMessageTemplateResponse:
    """Update a welcome message template."""
    service = TemplateService(db)
    template = await service.update_template(template_id, template_update)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )

    return template


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete template",
    description="Delete a welcome message template",
)
async def delete_template(
    template_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a welcome message template."""
    service = TemplateService(db)
    deleted = await service.delete_template(template_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {template_id} not found",
        )
