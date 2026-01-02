"""API routes initialization."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from src.api.routes.admin import router as admin_router
from src.api.routes.bookings import router as bookings_router
from src.api.routes.consent import router as consent_router
from src.api.routes.experts import router as experts_router
from src.api.routes.prd import router as prd_router
from src.api.routes.sessions import router as sessions_router
from src.api.routes.templates import router as templates_router
from src.api.routes.uploads import router as uploads_router
from src.core.config import settings
from src.core.database import AsyncSessionLocal
from src.core.security import require_admin_auth
from src.services.cache_service import CACHE_PREFIXES, cache_service

# Create main router
router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
router.include_router(experts_router, prefix="/experts", tags=["experts"])
router.include_router(prd_router, prefix="/prd", tags=["prd"])
router.include_router(bookings_router, prefix="/bookings", tags=["bookings"])
router.include_router(consent_router, prefix="/consent", tags=["consent"])
router.include_router(templates_router, prefix="/templates", tags=["templates"])
router.include_router(uploads_router, prefix="/uploads", tags=["uploads"])
router.include_router(admin_router, tags=["admin"])


async def check_database_health() -> str:
    """Check database connectivity."""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            if result.scalar() == 1:
                return "healthy"
    except Exception:
        pass
    return "unhealthy"


async def check_redis_health() -> str:
    """Check Redis connectivity."""
    try:
        import redis
        client = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=2)
        if client:
            client.ping()  # type: ignore[no-untyped-call]
        return "healthy"
    except redis.exceptions.ConnectionError:
        return "unavailable"
    except Exception:
        return "unhealthy"


@router.get("/health")
async def health_check():
    """Health check endpoint with system status.

    Returns:
        Dictionary containing:
        - status: Overall system status (operational, degraded, down)
        - version: API version
        - timestamp: Current timestamp
        - database: Database connection status
        - redis: Redis connection status
    """
    db_status = await check_database_health()
    redis_status = await check_redis_health()

    # Determine overall status
    if db_status == "healthy" and redis_status in ["healthy", "unavailable"]:
        overall_status = "operational"
    elif db_status == "healthy":
        overall_status = "degraded"
    else:
        overall_status = "down"

    return {
        "status": overall_status,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "redis": redis_status,
    }


# Cache management endpoints (admin only)

@router.get("/cache/status")
async def cache_status(admin_data: dict = Depends(require_admin_auth)):
    """Get cache status and statistics."""
    try:
        # Test Redis connection
        await cache_service.connect()

        # Get cache statistics
        stats: dict[str, object] = {
            "status": "healthy",
            "prefixes": CACHE_PREFIXES,
            "total_keys": 0,
            "key_counts": {}
        }

        # Count keys by prefix
        for prefix_name, prefix_value in CACHE_PREFIXES.items():
            keys = await cache_service.keys(f"{prefix_value}*")
            stats["key_counts"][prefix_name] = len(keys)  # type: ignore[index]
            stats["total_keys"] = int(stats["total_keys"]) + len(keys)  # type: ignore[index]

        return stats
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.delete("/cache/clear/{prefix}")
async def clear_cache_prefix(
    prefix: str,
    admin_data: dict = Depends(require_admin_auth)
):
    """Clear all cache entries for a specific prefix."""
    if prefix not in CACHE_PREFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid prefix. Valid prefixes: {list(CACHE_PREFIXES.keys())}"
        )

    pattern = f"{CACHE_PREFIXES[prefix]}*"
    deleted = await cache_service.delete_pattern(pattern)

    return {
        "message": f"Cleared {deleted} cache entries",
        "prefix": prefix,
        "pattern": pattern
    }


@router.get("/cache/test")
async def test_cache(admin_data: dict = Depends(require_admin_auth)):
    """Test cache functionality."""
    try:
        test_key = "test:cache_functionality"
        test_data = {"test": "data", "timestamp": datetime.utcnow().isoformat()}

        # Test set
        set_result = await cache_service.set(test_key, test_data, 60)

        # Test get
        get_result = await cache_service.get(test_key)

        # Test delete
        delete_result = await cache_service.delete(test_key)

        return {
            "set_result": set_result,
            "get_result": get_result,
            "delete_result": delete_result,
            "test_data": test_data
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
