"""
Admin API routes for expert management and system administration.
"""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.core.security import require_admin_auth, security
from src.schemas.expert import ExpertCreate, ExpertResponse, ExpertUpdate
from src.services.analytics_service import AnalyticsService
from src.services.cleanup_service import CleanupService
from src.services.expert_service import ExpertService
from src.services.session_service import SessionService

router = APIRouter(prefix="/admin", tags=["admin"])


async def verify_admin_access(
    x_admin_token: str = Header(None, alias="X-Admin-Token"),
    security: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verify admin access via header or bearer token.

    Priority: X-Admin-Token header > Bearer token
    """
    from src.core.security import AdminSecurity

    # If X-Admin-Token header is provided, verify it
    if x_admin_token:
        token_data = AdminSecurity.verify_admin_token(x_admin_token)
        if token_data:
            return token_data

    # Otherwise check bearer token
    if security:
        token_data = AdminSecurity.verify_admin_token(security.credentials)
        if token_data:
            return token_data

    # No valid authentication
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Admin authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/experts", response_model=list[ExpertResponse])
async def list_all_experts(
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
) -> list[ExpertResponse]:
    """List all experts for admin management (requires authentication).

    Returns:
        List of all expert profiles with full details
    """
    service = ExpertService(db)
    experts = await service.list_experts(include_inactive=True)
    return experts


@router.post("/experts", response_model=ExpertResponse, status_code=status.HTTP_201_CREATED)
async def create_expert_admin(
    expert_create: ExpertCreate,
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
) -> ExpertResponse:
    """Create new expert (admin only, requires authentication).

    Args:
        expert_create: Expert creation data
        admin_data: Admin authentication data
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
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
) -> ExpertResponse:
    """Update expert profile (admin only, requires authentication).

    Args:
        expert_id: Expert UUID
        expert_update: Updated expert data
        admin_data: Admin authentication data
        db: Database session

    Returns:
        Updated expert profile
    """
    service = ExpertService(db)
    expert = await service.get_expert_model(expert_id)
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
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Delete expert profile (admin only, requires authentication).

    Args:
        expert_id: Expert UUID to delete
        admin_data: Admin authentication data
        db: Database session

    Returns:
        Success message
    """
    service = ExpertService(db)
    expert = await service.get_expert_model(expert_id)
    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found"
        )
    await service.delete_expert(expert)
    return {"message": "Expert deleted successfully"}


@router.get("/analytics")
async def get_admin_analytics(
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Get system analytics and metrics for admins (requires authentication).

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
        ) from e


@router.get("/analytics/conversations")
async def get_conversation_analytics(
    days_back: int = 30,
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed conversation analytics (requires authentication).

    Args:
        days_back: Number of days to look back (default: 30)
        admin_data: Admin authentication data

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
        ) from e


@router.get("/analytics/experts")
async def get_expert_analytics(
    days_back: int = 30,
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Get expert performance analytics (requires authentication).

    Args:
        days_back: Number of days to look back (default: 30)
        admin_data: Admin authentication data

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
        ) from e


@router.get("/analytics/bookings")
async def get_booking_analytics(
    days_back: int = 30,
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Get booking performance analytics (requires authentication).

    Args:
        days_back: Number of days to look back (default: 30)
        admin_data: Admin authentication data

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
        ) from e


@router.get("/analytics/health")
async def get_system_health(
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Get system health and performance status (requires authentication).

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
        ) from e


@router.post("/auth/token")
async def create_admin_token(
    username: str,
    password: str,
):
    """Create an admin authentication token.

    Note: In production, use proper authentication like OAuth2 or JWT.
    This is a simplified implementation for the feature requirement.

    Args:
        username: Admin username
        password: Admin password

    Returns:
        Admin token
    """
    # Simple credential check (in production, use proper password hashing)
    # For demo purposes, accept any non-empty credentials
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password required"
        )

    from src.core.security import AdminSecurity

    # In production, verify against hashed password in database
    # For now, generate token for any valid credentials
    token = AdminSecurity.create_admin_token(username)

    return {
        "token": token,
        "token_type": "bearer",
        "expires_in": 3600  # 1 hour
    }


@router.post("/auth/revoke")
async def revoke_admin_token(
    token: str,
    admin_data: dict = Depends(verify_admin_access),
):
    """Revoke an admin token.

    Args:
        token: Token to revoke
        admin_data: Current admin authentication data

    Returns:
        Success message
    """
    from src.core.security import AdminSecurity

    AdminSecurity.revoke_token(token)

    return {"message": "Token revoked successfully"}


@router.post("/cleanup/sessions")
async def cleanup_old_sessions(
    max_age_days: int = 7,
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Clean up sessions older than specified days.

    Args:
        max_age_days: Maximum age in days for sessions to keep (default: 7)
        admin_data: Admin authentication data
        db: Database session

    Returns:
        Number of sessions deleted and cleanup details
    """
    try:
        cleanup_service = CleanupService(db)
        deleted_count = await cleanup_service.cleanup_old_sessions(max_age_days=max_age_days)

        return {
            "message": f"Cleaned up {deleted_count} old sessions",
            "deleted_count": deleted_count,
            "max_age_days": max_age_days,
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup sessions: {str(e)}"
        ) from e


@router.post("/cleanup/prds")
async def cleanup_expired_prds(
    max_age_days: int = 90,
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Clean up PRDs older than specified days.

    Args:
        max_age_days: Maximum age in days for PRDs to keep (default: 90)
        admin_data: Admin authentication data
        db: Database session

    Returns:
        Number of PRDs deleted and cleanup details
    """
    try:
        cleanup_service = CleanupService(db)
        deleted_count = await cleanup_service.cleanup_expired_prds(max_age_days=max_age_days)

        return {
            "message": f"Cleaned up {deleted_count} expired PRDs",
            "deleted_count": deleted_count,
            "max_age_days": max_age_days,
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup PRDs: {str(e)}"
        ) from e


@router.post("/cleanup/orphaned")
async def cleanup_orphaned_data(
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Clean up orphaned data (messages and PRDs without sessions).

    Args:
        admin_data: Admin authentication data
        db: Database session

    Returns:
        Cleanup results for orphaned data
    """
    try:
        cleanup_service = CleanupService(db)
        result = await cleanup_service.cleanup_orphaned_data()

        return {
            "message": "Cleaned up orphaned data",
            "orphaned_messages_deleted": result["messages_deleted"],
            "orphaned_prds_deleted": result["prds_deleted"],
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup orphaned data: {str(e)}"
        ) from e


@router.get("/cleanup/stats")
async def get_cleanup_stats(
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Get cleanup statistics and session lifecycle metrics.

    Args:
        admin_data: Admin authentication data
        db: Database session

    Returns:
        Session statistics and cleanup recommendations
    """
    try:
        cleanup_service = CleanupService(db)
        stats = await cleanup_service.get_session_stats()

        # Add cleanup recommendations
        recommendations = []
        if stats.get("sessions_older_than_7_days", 0) > 100:
            recommendations.append("Consider running session cleanup - many old sessions found")
        if stats.get("sessions_older_than_30_days", 0) > 50:
            recommendations.append("Many very old sessions - cleanup recommended")

        return {
            "session_stats": stats,
            "recommendations": recommendations,
            "cleanup_endpoints": [
                "/api/v1/admin/cleanup/sessions",
                "/api/v1/admin/cleanup/prds",
                "/api/v1/admin/cleanup/orphaned"
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cleanup stats: {str(e)}"
        ) from e


@router.get("/export/leads")
async def export_leads(
    min_lead_score: int = 50,
    days_back: int = 30,
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Export lead data as JSON (for CSV conversion).

    Returns lead data for sessions that qualify as potential leads based on:
    - Lead score >= min_lead_score
    - Sessions with bookings
    - Sessions with PRDs

    Args:
        min_lead_score: Minimum lead score threshold (default: 50)
        days_back: Look back period in days (default: 30)
        admin_data: Admin authentication data
        db: Database session

    Returns:
        List of lead data dictionaries
    """
    try:
        service = SessionService(db)
        leads = await service.get_lead_data(min_lead_score=min_lead_score, days_back=days_back)

        return {
            "leads": leads,
            "count": len(leads),
            "filters": {
                "min_lead_score": min_lead_score,
                "days_back": days_back
            },
            "export_info": {
                "message": "Use /api/v1/admin/export/leads/csv for CSV format",
                "csv_endpoint": "/api/v1/admin/export/leads/csv"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export leads: {str(e)}"
        ) from e


@router.get("/export/leads/csv")
async def export_leads_csv(
    min_lead_score: int = 50,
    days_back: int = 30,
    admin_data: dict = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """Export lead data as CSV.

    Returns a CSV file with lead data for sessions that qualify as potential leads.

    Args:
        min_lead_score: Minimum lead score threshold (default: 50)
        days_back: Look back period in days (default: 30)
        admin_data: Admin authentication data
        db: Database session

    Returns:
        CSV file download
    """
    try:
        service = SessionService(db)
        leads = await service.get_lead_data(min_lead_score=min_lead_score, days_back=days_back)

        # Generate CSV content
        headers = [
            "Visitor ID", "Session ID", "Created At", "Status", "Current Phase",
            "Lead Score", "Recommended Service", "Has Booking", "Has PRD",
            "Matched Expert", "Source URL", "Business Context"
        ]

        csv_lines = [",".join(headers)]

        for lead in leads:
            row = [
                lead.get("visitor_id", ""),
                lead.get("session_id", ""),
                lead.get("created_at", ""),
                lead.get("status", ""),
                lead.get("current_phase", ""),
                str(lead.get("lead_score", "")),
                lead.get("recommended_service", ""),
                "Yes" if lead.get("has_booking") else "No",
                "Yes" if lead.get("has_prd") else "No",
                lead.get("matched_expert", ""),
                lead.get("source_url", ""),
                f'"{lead.get("business_context", "")}"'.replace('"', '""'),
            ]
            # Escape commas in values
            row = [f'"{str(v).replace(chr(34), chr(34)*2)}"' for v in row]
            csv_lines.append(",".join(row))

        csv_content = "\n".join(csv_lines)

        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="leads_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv"'
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export leads as CSV: {str(e)}"
        ) from e
