"""Unit tests for session cleanup service."""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.models.prd import PRDDocument
from src.models.session import ConversationSession, Message, SessionStatus
from src.services.cleanup_service import CleanupService


@pytest.mark.asyncio
async def test_cleanup_old_sessions():
    """Test cleaning up sessions older than 7 days."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        from src.core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        cleanup_service = CleanupService(session)

        # Create old completed session (8 days old)
        old_session = ConversationSession(
            visitor_id="old-visitor",
            status="completed",
            completed_at=datetime.utcnow() - timedelta(days=8)
        )
        session.add(old_session)

        # Create old abandoned session (8 days old)
        old_abandoned = ConversationSession(
            visitor_id="old-abandoned",
            status="abandoned",
            completed_at=datetime.utcnow() - timedelta(days=8)
        )
        session.add(old_abandoned)

        # Create recent completed session (1 day old)
        recent_session = ConversationSession(
            visitor_id="recent-visitor",
            status="completed",
            completed_at=datetime.utcnow() - timedelta(days=1)
        )
        session.add(recent_session)

        # Create active session (should not be deleted)
        active_session = ConversationSession(
            visitor_id="active-visitor",
            status="active"
        )
        session.add(active_session)

        await session.commit()

        # Run cleanup
        deleted_count = await cleanup_service.cleanup_old_sessions(max_age_days=7)

        # Verify old sessions were deleted
        assert deleted_count == 2

        # Verify recent and active sessions still exist
        remaining_sessions = await session.execute(
            select(ConversationSession)
        )
        remaining_count = len(remaining_sessions.scalars().all())
        assert remaining_count == 2


@pytest.mark.asyncio
async def test_cleanup_expired_prds():
    """Test cleaning up PRDs older than 90 days."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        from src.core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        cleanup_service = CleanupService(session)

        # Create old PRD (91 days old)
        old_session = ConversationSession(visitor_id="test-visitor")
        session.add(old_session)
        await session.commit()

        old_prd = PRDDocument(
            session_id=old_session.id,
            content_markdown="# Old PRD",
            created_at=datetime.utcnow() - timedelta(days=91)
        )
        session.add(old_prd)

        # Create recent PRD (1 day old)
        recent_session = ConversationSession(visitor_id="test-visitor")
        session.add(recent_session)
        await session.commit()

        recent_prd = PRDDocument(
            session_id=recent_session.id,
            content_markdown="# Recent PRD",
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        session.add(recent_prd)

        await session.commit()

        # Run cleanup
        deleted_count = await cleanup_service.cleanup_expired_prds(max_age_days=90)

        # Verify old PRD was deleted
        assert deleted_count == 1

        # Verify recent PRD still exists
        remaining_prds = await session.execute(select(PRDDocument))
        remaining_count = len(remaining_prds.scalars().all())
        assert remaining_count == 1


@pytest.mark.asyncio
async def test_cleanup_orphaned_data():
    """Test cleaning up orphaned messages and PRDs."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        from src.core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        cleanup_service = CleanupService(session)

        # Create orphaned message (no session)
        orphaned_message = Message(
            session_id=uuid4(),  # Non-existent session ID
            role="user",
            content="Orphaned message"
        )
        session.add(orphaned_message)

        # Create orphaned PRD (no session)
        orphaned_prd = PRDDocument(
            session_id=uuid4(),  # Non-existent session ID
            content_markdown="# Orphaned PRD"
        )
        session.add(orphaned_prd)

        # Create valid session with message and PRD
        valid_session = ConversationSession(visitor_id="valid-visitor")
        session.add(valid_session)
        await session.commit()

        valid_message = Message(
            session_id=valid_session.id,
            role="user",
            content="Valid message"
        )
        session.add(valid_message)

        valid_prd = PRDDocument(
            session_id=valid_session.id,
            content_markdown="# Valid PRD"
        )
        session.add(valid_prd)

        await session.commit()

        # Run cleanup
        result = await cleanup_service.cleanup_orphaned_data()

        # Verify orphaned data was deleted
        assert result["messages_deleted"] == 1
        assert result["prds_deleted"] == 1

        # Verify valid data still exists
        valid_messages = await session.execute(
            select(Message).where(Message.session_id == valid_session.id)
        )
        assert len(valid_messages.scalars().all()) == 1

        valid_prds = await session.execute(
            select(PRDDocument).where(PRDDocument.session_id == valid_session.id)
        )
        assert len(valid_prds.scalars().all()) == 1