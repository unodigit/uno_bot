"""Application configuration and settings."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "UnoBot"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Server
    backend_port: int = 8001
    frontend_port: int = 5173
    allowed_origins: str = "http://localhost:5173,http://localhost:5180,http://localhost:3000"

    # Database
    database_url: str = "sqlite+aiosqlite:///./unobot.db"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Security
    secret_key: str = "change-this-to-a-secure-random-string"
    session_expiry_days: int = 7
    algorithm: str = "HS256"

    # Anthropic AI
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Google Calendar
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str = "http://localhost:8001/api/v1/auth/google/callback"

    # SendGrid
    sendgrid_api_key: str | None = None
    sendgrid_from_email: str = "noreply@unodigit.com"

    # AWS S3 / Cloudflare R2
    s3_bucket_name: str = "unobot-documents"
    s3_region: str = "us-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    # File paths
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    logs_dir: Path = base_dir / "logs"
    reports_dir: Path = base_dir / "reports"

    # PRD settings
    prd_expiry_days: int = 90

    # Calendar settings
    booking_buffer_minutes: int = 15
    availability_days_ahead: int = 14
    min_slots_to_show: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
