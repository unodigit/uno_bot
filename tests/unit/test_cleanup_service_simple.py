"""Simple test to debug session stats issue."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.models.session import ConversationSession, SessionStatus
from src.services.cleanup_service import CleanupService


@pytest.mark.asyncio
async def test_get_session_stats_simple():
    """Simple test for session stats."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        from src.core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        cleanup_service = CleanupService(session)

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

        # Test stats
        stats = await cleanup_service.get_session_stats()
        print(f"Stats: {stats}")

        assert "total_sessions" in stats
        assert stats["total_sessions"] == 2
        assert stats["active_sessions"] == 1
        assert stats["completed_sessions"] == 1