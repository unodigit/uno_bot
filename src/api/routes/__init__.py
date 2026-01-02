"""API routes initialization."""
from fastapi import APIRouter

from src.api.routes.admin import router as admin_router
from src.api.routes.bookings import router as bookings_router
from src.api.routes.experts import router as experts_router
from src.api.routes.prd import router as prd_router
from src.api.routes.sessions import router as sessions_router
from src.api.routes.templates import router as templates_router

# Create main router
router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
router.include_router(experts_router, prefix="/experts", tags=["experts"])
router.include_router(prd_router, prefix="/prd", tags=["prd"])
router.include_router(bookings_router, prefix="/bookings", tags=["bookings"])
router.include_router(templates_router, prefix="/templates", tags=["templates"])
router.include_router(admin_router, tags=["admin"])

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
