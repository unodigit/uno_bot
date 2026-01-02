"""
UnoBot - AI Business Consultant & Appointment Booking System

Main FastAPI application with OpenAPI documentation.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.routes import router
from src.core.config import settings
from src.core.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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

# Serve static files
app.mount("/static", StaticFiles(directory=settings.base_dir / "src" / "static"), name="static")


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
