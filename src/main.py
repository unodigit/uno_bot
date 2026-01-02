"""
UnoBot - AI Business Consultant & Appointment Booking System

Main FastAPI application with OpenAPI documentation.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket as FastAPIWebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from socketio import AsyncServer

from src.api.routes import router
from src.core.config import settings
from src.core.database import init_db, AsyncSessionLocal
from src.core.exception_handlers import register_exception_handlers
from src.api.routes.websocket import manager, handle_chat_message, handle_generate_prd, handle_match_experts, handle_get_availability, handle_create_booking

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Socket.IO server
sio = AsyncServer(
    cors_allowed_origins=settings.allowed_origins.split(","),
    async_mode="asgi",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """Application lifespan events."""
    # Startup
    logger.info("Starting UnoBot API...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down UnoBot API...")


# Create FastAPI application
app = FastAPI(
    title="UnoBot API",
    description="""
    UnoBot is an AI-powered business consultant chatbot that transforms website
    visitors into qualified leads by conducting intelligent business discovery
    conversations, automatically generating Project Requirements Documents (PRDs),
    and seamlessly booking appointments with UnoDigit professionals.

    ## Features

    - **Chat Sessions**: Real-time AI-powered conversations with streaming responses
    - **PRD Generation**: Automatic Project Requirements Document generation
    - **Expert Matching**: Intelligent matching with UnoDigit professionals
    - **Calendar Integration**: Google Calendar integration for appointment booking
    - **Email Notifications**: Automated booking confirmations and reminders

    ## Authentication

    Most endpoints require a session ID passed in the `X-Session-ID` header.
    Admin endpoints require JWT authentication.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Register exception handlers
register_exception_handlers(app)

# Serve static files
app.mount("/static", StaticFiles(directory=settings.base_dir / "src" / "static"), name="static")

# Socket.IO Event Handlers

@sio.on("connect")
async def handle_connect(sid: str, environ: dict) -> None:
    """Handle Socket.IO connection."""
    # Extract session_id from query params
    query = environ.get("QUERY_STRING", "")
    session_id = None
    for param in query.split("&"):
        if param.startswith("session_id="):
            session_id = param.split("=")[1]
            break

    if session_id:
        # Store session_id with connection
        await sio.save_session(sid, {"session_id": session_id})
        logger.info(f"Socket.IO client {sid} connected for session {session_id}")
    else:
        logger.warning(f"Socket.IO client {sid} connected without session_id")


@sio.on("disconnect")
async def handle_disconnect(sid: str) -> None:
    """Handle Socket.IO disconnection."""
    session_data = await sio.get_session(sid)
    if session_data and "session_id" in session_data:
        session_id = session_data["session_id"]
        manager.disconnect(session_id)
        logger.info(f"Socket.IO client {sid} disconnected from session {session_id}")


@sio.on("join_session")
async def handle_join_session(sid: str, data: dict) -> None:
    """Client joins a session."""
    session_id = data.get("session_id")
    if not session_id:
        await sio.emit("error", {"message": "session_id required"}, room=sid)
        return

    # Store session_id in connection data
    await sio.save_session(sid, {"session_id": session_id})

    # Join the room
    await sio.enter_room(sid, session_id)

    # Send connected event back to client
    await sio.emit("connected", {"session_id": session_id}, room=sid)
    logger.info(f"Client {sid} joined session {session_id}")


@sio.on("send_message")
async def handle_socket_message(sid: str, data: dict) -> None:
    """Handle incoming chat message via WebSocket."""
    session_data = await sio.get_session(sid)
    session_id = session_data.get("session_id") if session_data else None

    if not session_id:
        await sio.emit("error", {"message": "Not connected to a session"}, room=sid)
        return

    content = data.get("content")
    if not content:
        await sio.emit("error", {"message": "content required"}, room=sid)
        return

    # Get database session
    async with AsyncSessionLocal() as db:
        try:
            # Send typing indicator
            await sio.emit("typing_start", {"from": "bot"}, room=session_id)

            # Handle the message
            result = await handle_chat_message(session_id, content, db)

            # Stop typing indicator
            await sio.emit("typing_stop", {"from": "bot"}, room=session_id)

            # Send the complete response
            await sio.emit("message", {
                "user_message": result["user_message"],
                "ai_message": result["ai_message"],
            }, room=session_id)

            # Send phase change if applicable
            if result["session"].get("current_phase"):
                await sio.emit("phase_change", {
                    "phase": result["session"]["current_phase"]
                }, room=session_id)

            # Check if PRD is ready to be generated
            session = result["session"]
            if (session.get("client_info", {}).get("name") and
                session.get("business_context", {}).get("challenges") and
                not session.get("prd_id")):
                await sio.emit("prd_ready", {
                    "message": "PRD can now be generated"
                }, room=session_id)

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await sio.emit("error", {"message": str(e)}, room=session_id)


@sio.on("generate_prd")
async def handle_socket_prd(sid: str, data: dict) -> None:
    """Handle PRD generation via WebSocket."""
    session_data = await sio.get_session(sid)
    session_id = session_data.get("session_id") if session_data else None

    if not session_id:
        await sio.emit("error", {"message": "Not connected to a session"}, room=sid)
        return

    async with AsyncSessionLocal() as db:
        try:
            result = await handle_generate_prd(session_id, db)
            await sio.emit("prd_generated", result, room=session_id)
        except ValueError as e:
            await sio.emit("error", {"message": str(e)}, room=session_id)
        except Exception as e:
            logger.error(f"Error generating PRD: {e}")
            await sio.emit("error", {"message": "Failed to generate PRD"}, room=session_id)


@sio.on("match_experts")
async def handle_socket_match_experts(sid: str, data: dict) -> None:
    """Handle expert matching via WebSocket."""
    session_data = await sio.get_session(sid)
    session_id = session_data.get("session_id") if session_data else None

    if not session_id:
        await sio.emit("error", {"message": "Not connected to a session"}, room=sid)
        return

    async with AsyncSessionLocal() as db:
        try:
            result = await handle_match_experts(session_id, db)
            await sio.emit("experts_matched", result, room=session_id)
        except Exception as e:
            logger.error(f"Error matching experts: {e}")
            await sio.emit("error", {"message": "Failed to match experts"}, room=session_id)


@sio.on("get_availability")
async def handle_socket_availability(sid: str, data: dict) -> None:
    """Handle availability request via WebSocket."""
    session_data = await sio.get_session(sid)
    session_id = session_data.get("session_id") if session_data else None

    if not session_id:
        await sio.emit("error", {"message": "Not connected to a session"}, room=sid)
        return

    expert_id = data.get("expert_id")
    timezone = data.get("timezone", "UTC")

    if not expert_id:
        await sio.emit("error", {"message": "expert_id required"}, room=sid)
        return

    async with AsyncSessionLocal() as db:
        try:
            result = await handle_get_availability(expert_id, timezone, db)
            await sio.emit("availability", result, room=session_id)
        except Exception as e:
            logger.error(f"Error getting availability: {e}")
            await sio.emit("error", {"message": "Failed to get availability"}, room=session_id)


@sio.on("create_booking")
async def handle_socket_booking(sid: str, data: dict) -> None:
    """Handle booking creation via WebSocket."""
    session_data = await sio.get_session(sid)
    session_id = session_data.get("session_id") if session_data else None

    if not session_id:
        await sio.emit("error", {"message": "Not connected to a session"}, room=sid)
        return

    required_fields = ["expert_id", "start_time", "end_time", "timezone", "client_name", "client_email"]
    for field in required_fields:
        if field not in data:
            await sio.emit("error", {"message": f"{field} required"}, room=sid)
            return

    async with AsyncSessionLocal() as db:
        try:
            result = await handle_create_booking(session_id, data, db)
            await sio.emit("booking_confirmed", result, room=session_id)
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            await sio.emit("error", {"message": "Failed to create booking"}, room=session_id)


# Mount Socket.IO ASGI app
app.mount("/ws", sio)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=settings.debug,
    )
