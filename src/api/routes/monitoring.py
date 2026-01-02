"""Monitoring and metrics API endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.schemas.monitoring import SystemMetricsResponse, HealthStatusResponse, EndpointMetricsResponse
from src.services.monitoring_service import MonitoringService, get_monitoring_service

router = APIRouter()


@router.get("/metrics", response_model=SystemMetricsResponse, tags=["monitoring"])
async def get_system_metrics(
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
):
    """Get current system metrics and performance data."""
    try:
        metrics = monitoring_service.get_system_metrics()
        return SystemMetricsResponse(
            success=True,
            data={
                "timestamp": metrics.timestamp.isoformat(),
                "request_metrics": {
                    "total_requests": metrics.total_requests,
                    "successful_requests": metrics.successful_requests,
                    "failed_requests": metrics.failed_requests,
                    "average_response_time": metrics.average_response_time,
                    "p95_response_time": metrics.p95_response_time,
                },
                "database_metrics": {
                    "size_mb": metrics.database_size_mb,
                    "active_connections": metrics.active_connections,
                },
                "session_metrics": {
                    "active_sessions": metrics.active_sessions,
                    "sessions_last_hour": metrics.sessions_last_hour,
                },
                "business_metrics": {
                    "total_messages": metrics.total_messages,
                    "prd_generated": metrics.prd_generated,
                    "bookings_created": metrics.bookings_created,
                    "expert_matches": metrics.expert_matches,
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/metrics/endpoints", response_model=EndpointMetricsResponse, tags=["monitoring"])
async def get_endpoint_metrics(
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
):
    """Get metrics per endpoint."""
    try:
        endpoint_metrics = monitoring_service.get_endpoint_metrics()
        return EndpointMetricsResponse(
            success=True,
            data=endpoint_metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get endpoint metrics: {str(e)}")


@router.get("/health", response_model=HealthStatusResponse, tags=["monitoring"])
async def get_health_status(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    db: AsyncSession = Depends(get_db)
):
    """Get application health status."""
    try:
        health_status = monitoring_service.get_health_status()

        # Add database check
        try:
            # Simple database connectivity test
            await db.execute("SELECT 1")
            db_status = "ok"
            db_message = "Database connection healthy"
        except Exception as e:
            db_status = "error"
            db_message = f"Database connection failed: {str(e)}"

        # Update health status with database info
        if "database" in health_status["checks"]:
            health_status["checks"]["database"]["status"] = db_status
            health_status["checks"]["database"]["message"] = db_message

        return HealthStatusResponse(
            success=True,
            data=health_status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/health/detailed", response_model=HealthStatusResponse, tags=["monitoring"])
async def get_detailed_health_status(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed application health status with all checks."""
    try:
        health_status = monitoring_service.get_health_status()

        # Add detailed database information
        try:
            # Database connectivity test
            await db.execute("SELECT 1")

            # Database size check
            from src.core.database import get_database_size
            db_size = get_database_size()

            # Database connection pool status (if using connection pooling)
            db_status = "ok"
            db_message = f"Database healthy, size: {db_size:.2f}MB"
        except Exception as e:
            db_status = "error"
            db_message = f"Database issues detected: {str(e)}"

        # Add system resource checks
        try:
            import psutil
            memory_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)

            system_status = "ok" if memory_info.percent < 80 and cpu_percent < 80 else "warning"
            system_message = f"Memory: {memory_info.percent:.1f}%, CPU: {cpu_percent:.1f}%"

            # Add system metrics to health status
            health_status["system"] = {
                "status": system_status,
                "message": system_message,
                "memory_percent": memory_info.percent,
                "cpu_percent": cpu_percent,
                "disk_usage": psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else None
            }
        except ImportError:
            health_status["system"] = {
                "status": "unknown",
                "message": "System monitoring not available (psutil not installed)"
            }

        # Update database check
        if "database" in health_status["checks"]:
            health_status["checks"]["database"]["status"] = db_status
            health_status["checks"]["database"]["message"] = db_message

        # Determine overall status
        overall_status = "healthy"
        for check in health_status["checks"].values():
            if check.get("status") == "error":
                overall_status = "error"
                break
            elif check.get("status") == "warning" and overall_status == "healthy":
                overall_status = "warning"

        health_status["status"] = overall_status

        return HealthStatusResponse(
            success=True,
            data=health_status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detailed health check failed: {str(e)}")


@router.get("/metrics/summary", response_model=SystemMetricsResponse, tags=["monitoring"])
async def get_metrics_summary(
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
):
    """Get a summary of key metrics for dashboard display."""
    try:
        metrics = monitoring_service.get_system_metrics()

        # Calculate key ratios
        success_rate = (metrics.successful_requests / max(metrics.total_requests, 1)) * 100
        session_conversion = (metrics.bookings_created / max(metrics.active_sessions, 1)) * 100

        summary_data = {
            "timestamp": metrics.timestamp.isoformat(),
            "key_metrics": {
                "active_sessions": metrics.active_sessions,
                "total_requests": metrics.total_requests,
                "success_rate": round(success_rate, 2),
                "avg_response_time": round(metrics.average_response_time, 3),
                "p95_response_time": round(metrics.p95_response_time, 3),
                "bookings_per_hour": metrics.bookings_created,
                "session_conversion_rate": round(session_conversion, 2)
            },
            "business_metrics": {
                "total_messages": metrics.total_messages,
                "prd_generated": metrics.prd_generated,
                "bookings_created": metrics.bookings_created,
                "expert_matches": metrics.expert_matches,
            }
        }

        return SystemMetricsResponse(
            success=True,
            data=summary_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics summary: {str(e)}")