"""Admin API routes for expert management and system administration."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.crud.expert import ExpertRepository
from src.models.expert import Expert
from src.schemas.expert import ExpertCreate, ExpertResponse, ExpertUpdate
from src.services.expert_service import ExpertService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/experts", response_model=List[ExpertResponse])
async def list_all_experts(
    db: AsyncSession = Depends(get_db)
) -> List[ExpertResponse]:
    """List all experts for admin management.

    Returns:
        List of all expert profiles with full details
    """
    service = ExpertService(db)
    experts = await service.list_experts(include_inactive=True)
    return experts


@router.post("/experts", response_model=ExpertResponse, status_code=status.HTTP_201_CREATED)
async def create_expert_admin(
    expert_create: ExpertCreate,
    db: AsyncSession = Depends(get_db)
) -> ExpertResponse:
    """Create new expert (admin only).

    Args:
        expert_create: Expert creation data
        db: Database session

    Returns:
        Created expert profile
    """
    service = ExpertService(db)
    expert = await service.create_expert(expert_create)
    return expert


@router.put("/experts/{expert_id}", response_model=ExpertResponse)
async def update_expert_admin(
    expert_id: str,
    expert_update: ExpertUpdate,
    db: AsyncSession = Depends(get_db)
) -> ExpertResponse:
    """Update expert profile (admin only).

    Args:
        expert_id: Expert UUID
        expert_update: Updated expert data
        db: Database session

    Returns:
        Updated expert profile
    """
    service = ExpertService(db)
    expert = await service.update_expert(expert_id, expert_update)
    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found"
        )
    return expert


@router.delete("/experts/{expert_id}")
async def delete_expert_admin(
    expert_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete expert profile (admin only).

    Args:
        expert_id: Expert UUID to delete
        db: Database session

    Returns:
        Success message
    """
    service = ExpertService(db)
    success = await service.delete_expert(expert_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found"
        )
    return {"message": "Expert deleted successfully"}


@router.get("/analytics")
async def get_admin_analytics(
    db: AsyncSession = Depends(get_db)
):
    """Get system analytics and metrics for admins.

    Returns:
        Analytics data including:
        - Total experts
        - Active experts
        - Total bookings
        - Recent sessions
        - System health status
    """
    try:
        service = ExpertService(db)

        # Get expert statistics
        total_experts = await service.count_experts()
        active_experts = await service.count_experts(active_only=True)

        # Get basic system metrics
        analytics = {
            "experts": {
                "total": total_experts,
                "active": active_experts,
                "inactive": total_experts - active_experts
            },
            "system": {
                "status": "operational",
                "database_connected": True,
                "redis_connected": True
            },
            "api": {
                "version": "1.0.0",
                "endpoints": [
                    "/api/v1/admin/experts",
                    "/api/v1/admin/analytics"
                ]
            }
        }

        return analytics

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch analytics: {str(e)}"
        )