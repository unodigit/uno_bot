"""API routes initialization."""
from fastapi import APIRouter

from src.api.routes.sessions import router as sessions_router

# Create main router
router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
