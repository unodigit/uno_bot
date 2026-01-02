"""API routes initialization."""
from fastapi import APIRouter

from src.api.routes.experts import router as experts_router
from src.api.routes.prd import router as prd_router
from src.api.routes.sessions import router as sessions_router

# Create main router
router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
router.include_router(prd_router, prefix="/prd", tags=["prd"])
router.include_router(experts_router, prefix="/experts", tags=["experts"])

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
