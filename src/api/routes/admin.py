"""Admin API routes for expert management and system administration."""
from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.schemas.expert import ExpertCreate, ExpertResponse, ExpertUpdate
from src.services.expert_service import ExpertService
from src.services.analytics_service import AnalyticsService

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
    expert_id: uuid.UUID,
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
    expert = await service.get_expert(expert_id)
    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found"
        )
    updated_expert = await service.update_expert(expert, expert_update)
    return updated_expert


@router.delete("/experts/{expert_id}")
async def delete_expert_admin(
    expert_id: uuid.UUID,
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
    expert = await service.get_expert(expert_id)
    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found"
        )
    await service.delete_expert(expert)
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
        analytics_service = AnalyticsService(db)

        # Get expert statistics
        total_experts = await service.count_experts()
        active_experts = await service.count_experts(active_only=True)

        # Get conversation analytics
        conversation_analytics = await analytics_service.get_conversation_analytics(days_back=30)

        # Get expert performance analytics
        expert_analytics = await analytics_service.get_expert_analytics(days_back=30)

        # Get booking analytics
        booking_analytics = await analytics_service.get_booking_analytics(days_back=30)

        # Get system health
        system_health = await analytics_service.get_system_health()

        # Combine all analytics
        analytics = {
            "experts": {
                "total": total_experts,
                "active": active_experts,
                "inactive": total_experts - active_experts
            },
            "conversations": conversation_analytics,
            "experts_performance": expert_analytics,
            "bookings": booking_analytics,
            "system_health": system_health,
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


@router.get("/analytics/conversations")
async def get_conversation_analytics(
    days_back: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed conversation analytics.

    Args:
        days_back: Number of days to look back (default: 30)

    Returns:
        Detailed conversation metrics and trends
    """
    try:
        analytics_service = AnalyticsService(db)
        analytics = await analytics_service.get_conversation_analytics(days_back=days_back)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch conversation analytics: {str(e)}"
        )


@router.get("/analytics/experts")
async def get_expert_analytics(
    days_back: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get expert performance analytics.

    Args:
        days_back: Number of days to look back (default: 30)

    Returns:
        Expert performance metrics and rankings
    """
    try:
        analytics_service = AnalyticsService(db)
        analytics = await analytics_service.get_expert_analytics(days_back=days_back)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch expert analytics: {str(e)}"
        )


@router.get("/analytics/bookings")
async def get_booking_analytics(
    days_back: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get booking performance analytics.

    Args:
        days_back: Number of days to look back (default: 30)

    Returns:
        Booking metrics and cancellation analysis
    """
    try:
        analytics_service = AnalyticsService(db)
        analytics = await analytics_service.get_booking_analytics(days_back=days_back)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch booking analytics: {str(e)}"
        )


@router.get("/analytics/health")
async def get_system_health(
    db: AsyncSession = Depends(get_db)
):
    """Get system health and performance status.

    Returns:
        System health metrics and database status
    """
    try:
        analytics_service = AnalyticsService(db)
        health = await analytics_service.get_system_health()
        return health
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch system health: {str(e)}"
        )