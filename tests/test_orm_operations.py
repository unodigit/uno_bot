"""Test SQLAlchemy ORM operations comprehensively."""
import asyncio
import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload

from src.core.database import Base, get_db
from src.models.expert import Expert
from src.models.session import ConversationSession, Message, SessionStatus, SessionPhase, MessageRole
from src.models.booking import Booking, BookingStatus
from src.models.prd import PRDDocument


@pytest.mark.asyncio
async def test_create_conversation_session():
    """Test creating a conversation session with all fields."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create a session
        session_obj = ConversationSession(
            visitor_id="test_visitor_123",
            status=SessionStatus.ACTIVE.value,
            current_phase=SessionPhase.GREETING.value,
            client_info={"name": "Test User", "email": "test@example.com"},
            business_context={"industry": "Tech", "company_size": "100-500"},
            qualification={"budget": "50000", "timeline": "3 months"},
            lead_score=75,
            recommended_service="AI Strategy",
            source_url="http://localhost:5173",
            user_agent="TestAgent/1.0",
            email_opt_in=True,
        )

        session.add(session_obj)
        await session.commit()
        await session.refresh(session_obj)

        # Verify the session was created
        assert session_obj.id is not None
        assert session_obj.visitor_id == "test_visitor_123"
        assert session_obj.status == SessionStatus.ACTIVE.value
        assert session_obj.lead_score == 75
        assert session_obj.email_opt_in is True
        assert session_obj.started_at is not None
        assert session_obj.last_activity is not None


@pytest.mark.asyncio
async def test_session_with_messages():
    """Test creating a session with multiple messages."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create session
        session_obj = ConversationSession(
            visitor_id="test_visitor_456",
            status=SessionStatus.ACTIVE.value,
        )
        session.add(session_obj)
        await session.commit()
        await session.refresh(session_obj)

        # Create messages
        msg1 = Message(
            session_id=session_obj.id,
            role=MessageRole.USER.value,
            content="Hello, I need help with AI strategy",
            meta_data={"type": "greeting"},
        )
        msg2 = Message(
            session_id=session_obj.id,
            role=MessageRole.ASSISTANT.value,
            content="Hi! I'd be happy to help you with AI strategy.",
            meta_data={"type": "response"},
        )

        session.add(msg1)
        session.add(msg2)
        await session.commit()

        # Query messages using relationship
        await session.refresh(session_obj)
        messages = session_obj.messages

        assert len(messages) == 2
        assert messages[0].content == "Hello, I need help with AI strategy"
        assert messages[1].role == MessageRole.ASSISTANT.value


@pytest.mark.asyncio
async def test_expert_with_relationships():
    """Test creating an expert and related sessions/bookings."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create expert
        expert = Expert(
            name="Dr. Jane Smith",
            email="jane.smith@example.com",
            role="AI Strategy Consultant",
            bio="Expert in AI strategy and digital transformation",
            specialties=["AI Strategy", "Machine Learning", "Digital Transformation"],
            services=["AI Strategy & Planning", "Custom Development"],
            is_active=True,
        )
        session.add(expert)
        await session.commit()
        await session.refresh(expert)

        # Create session that matches to this expert
        session_obj = ConversationSession(
            visitor_id="test_visitor_789",
            status=SessionStatus.ACTIVE.value,
            matched_expert_id=expert.id,
            lead_score=85,
        )
        session.add(session_obj)
        await session.commit()

        # Create booking
        booking = Booking(
            session_id=session_obj.id,
            expert_id=expert.id,
            title="AI Strategy Consultation",
            start_time=datetime.utcnow() + timedelta(days=2),
            end_time=datetime.utcnow() + timedelta(days=2, hours=1),
            timezone="UTC",
            client_name="Test Client",
            client_email="client@example.com",
            status=BookingStatus.CONFIRMED.value,
        )
        session.add(booking)
        await session.commit()

        # Query relationships
        await session.refresh(expert)
        assert len(expert.sessions) == 1
        assert expert.sessions[0].visitor_id == "test_visitor_789"


@pytest.mark.asyncio
async def test_prd_document_creation():
    """Test creating a PRD document."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create session
        session_obj = ConversationSession(
            visitor_id="test_visitor_prd",
            status=SessionStatus.COMPLETED.value,
        )
        session.add(session_obj)
        await session.commit()
        await session.refresh(session_obj)

        # Create PRD
        prd = PRDDocument(
            session_id=session_obj.id,
            version=1,
            content_markdown="# Project Requirements Document\n\n## Executive Summary\n...",
            client_company="Acme Corp",
            client_name="John Doe",
            recommended_service="AI Strategy",
            matched_expert="Dr. Jane Smith",
        )
        session.add(prd)
        await session.commit()
        await session.refresh(prd)

        # Verify
        assert prd.id is not None
        assert prd.version == 1
        assert prd.client_company == "Acme Corp"
        assert prd.created_at is not None


@pytest.mark.asyncio
async def test_update_session_status():
    """Test updating session status and phase."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create session
        session_obj = ConversationSession(
            visitor_id="test_visitor_update",
            status=SessionStatus.ACTIVE.value,
            current_phase=SessionPhase.GREETING.value,
        )
        session.add(session_obj)
        await session.commit()
        await session.refresh(session_obj)

        # Update status
        session_obj.status = SessionStatus.COMPLETED.value
        session_obj.current_phase = SessionPhase.CONFIRMATION.value
        session_obj.completed_at = datetime.utcnow()
        await session.commit()
        await session.refresh(session_obj)

        # Verify update
        assert session_obj.status == SessionStatus.COMPLETED.value
        assert session_obj.current_phase == SessionPhase.CONFIRMATION.value
        assert session_obj.completed_at is not None


@pytest.mark.asyncio
async def test_query_with_filters():
    """Test querying with various filters."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create multiple sessions
        for i in range(5):
            session_obj = ConversationSession(
                visitor_id=f"visitor_{i}",
                status=SessionStatus.ACTIVE.value if i < 3 else SessionStatus.COMPLETED.value,
                lead_score=70 + i * 5,
            )
            session.add(session_obj)
        await session.commit()

        # Query active sessions
        from sqlalchemy import select
        result = await session.execute(
            select(ConversationSession).where(ConversationSession.status == SessionStatus.ACTIVE.value)
        )
        active_sessions = result.scalars().all()

        assert len(active_sessions) == 3

        # Query high lead score sessions
        result = await session.execute(
            select(ConversationSession).where(ConversationSession.lead_score >= 80)
        )
        high_score_sessions = result.scalars().all()

        assert len(high_score_sessions) == 3


@pytest.mark.asyncio
async def test_delete_operations():
    """Test delete operations with cascades."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create session with messages
        session_obj = ConversationSession(
            visitor_id="test_visitor_delete",
            status=SessionStatus.ACTIVE.value,
        )
        session.add(session_obj)
        await session.commit()
        await session.refresh(session_obj)

        msg = Message(
            session_id=session_obj.id,
            role=MessageRole.USER.value,
            content="Test message",
        )
        session.add(msg)
        await session.commit()

        # Delete session (should cascade or handle messages)
        await session.delete(session_obj)
        await session.commit()

        # Verify deletion
        result = await session.execute(
            select(ConversationSession).where(ConversationSession.id == session_obj.id)
        )
        assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_json_field_operations():
    """Test JSON field operations for client_info, business_context, etc."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create session with JSON fields
        session_obj = ConversationSession(
            visitor_id="test_visitor_json",
            client_info={
                "name": "Test User",
                "email": "test@example.com",
                "company": "Test Corp",
            },
            business_context={
                "industry": "Technology",
                "company_size": "100-500",
                "current_challenges": ["Scaling", "Efficiency"],
            },
            qualification={
                "budget": "$50,000-$100,000",
                "timeline": "3-6 months",
                "decision_maker": "CTO",
            },
        )
        session.add(session_obj)
        await session.commit()
        await session.refresh(session_obj)

        # Verify JSON data
        assert session_obj.client_info["name"] == "Test User"
        assert session_obj.business_context["industry"] == "Technology"
        assert session_obj.qualification["budget"] == "$50,000-$100,000"

        # Update JSON field
        session_obj.client_info["phone"] = "+1-555-0123"
        session_obj.qualification["timeline"] = "6-12 months"
        await session.commit()
        await session.refresh(session_obj)

        assert session_obj.client_info["phone"] == "+1-555-0123"
        assert session_obj.qualification["timeline"] == "6-12 months"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
