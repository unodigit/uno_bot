"""Integration tests for session cleanup feature."""
import pytest
from datetime import datetime, timedelta
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.core.database import get_db
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.models.session import ConversationSession, SessionStatus


@pytest.mark.asyncio
async def test_session_cleanup_endpoint():
    """Test the admin session cleanup endpoint."""
    # Use in-memory DB
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        from src.core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create test sessions
        # Old completed session (8 days old)
        old_session = ConversationSession(
            visitor_id="old-visitor",
            status=SessionStatus.COMPLETED.value,
            completed_at=datetime.utcnow() - timedelta(days=8)
        )
        session.add(old_session)

        # Recent completed session (1 day old)
        recent_session = ConversationSession(
            visitor_id="recent-visitor",
            status=SessionStatus.COMPLETED.value,
            completed_at=datetime.utcnow() - timedelta(days=1)
        )
        session.add(recent_session)

        # Active session (should not be deleted)
        active_session = ConversationSession(
            visitor_id="active-visitor",
            status=SessionStatus.ACTIVE.value
        )
        session.add(active_session)

        await session.commit()

        # Override DB dependency
        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db

        # Test cleanup endpoint
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # First, create an admin token
            token_response = await client.post("/api/v1/admin/auth/token", params={
                "username": "admin",
                "password": "password123"
            })
            print(f"Token response status: {token_response.status_code}")
            print(f"Token response content: {token_response.content}")
            assert token_response.status_code == 200
            admin_token = token_response.json()["token"]

            # Test cleanup endpoint with admin token
            cleanup_response = await client.post(
                "/api/v1/admin/cleanup/sessions",
                headers={"X-Admin-Token": admin_token},
                json={"max_age_days": 7}
            )

            assert cleanup_response.status_code == 200
            result = cleanup_response.json()
            assert result["deleted_count"] == 1
            assert result["message"] == "Cleaned up 1 old sessions"
            assert result["status"] == "completed"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cleanup_stats_endpoint():
    """Test the cleanup statistics endpoint."""
    # Use in-memory DB
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        from src.core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create test sessions
        old_session = ConversationSession(
            visitor_id="old-visitor",
            status=SessionStatus.COMPLETED.value,
            completed_at=datetime.utcnow() - timedelta(days=10)
        )
        session.add(old_session)

        active_session = ConversationSession(
            visitor_id="active-visitor",
            status=SessionStatus.ACTIVE.value
        )
        session.add(active_session)

        await session.commit()

        # Override DB dependency
        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create admin token
            token_response = await client.post("/api/v1/admin/auth/token", params={
                "username": "admin",
                "password": "password123"
            })
            assert token_response.status_code == 200
            admin_token = token_response.json()["token"]

            # Test stats endpoint
            stats_response = await client.get(
                "/api/v1/admin/cleanup/stats",
                headers={"X-Admin-Token": admin_token}
            )

            assert stats_response.status_code == 200
            stats = stats_response.json()

            assert "session_stats" in stats
            assert stats["session_stats"]["total_sessions"] == 2
            assert stats["session_stats"]["active_sessions"] == 1
            assert stats["session_stats"]["completed_sessions"] == 1
            assert stats["session_stats"]["sessions_older_than_7_days"] >= 1

            assert "recommendations" in stats
            assert "cleanup_endpoints" in stats

    app.dependency_overrides.clear()