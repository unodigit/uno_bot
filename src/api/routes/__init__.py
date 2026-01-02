"""API routes initialization."""
from fastapi import APIRouter

from src.api.routes.sessions import router as sessions_router

# Create main router
router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])

# Add WebSocket endpoint directly
from fastapi import WebSocket
from src.api.routes.websocket import websocket_endpoint

@router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    """WebSocket chat endpoint."""
    await websocket_endpoint(websocket, websocket.query_params.get("session_id"))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
