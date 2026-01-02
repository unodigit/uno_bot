"""Unit tests for SessionService."""
import uuid
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.session import MessageRole, SessionPhase, SessionStatus
from src.schemas.session import SessionCreate, MessageCreate
from src.services.session_service import SessionService


@pytest.mark.asyncio
async def test_create_session(db_session: AsyncSession, sample_visitor_id: str):
    """Test creating a new session."""
    service = SessionService(db_session)
    session_create = SessionCreate(
        visitor_id=sample_visitor_id,
        source_url="https://example.com",
        user_agent="TestAgent/1.0",
    )

    session = await service.create_session(session_create)

    assert session.visitor_id == sample_visitor_id
    assert session.status == SessionStatus.ACTIVE
    assert session.current_phase == SessionPhase.GREETING
    assert session.source_url == "https://example.com"
    assert session.user_agent == "TestAgent/1.0"
    assert session.started_at is not None
    assert session.last_activity is not None
    # Check welcome message was created
    assert len(session.messages) == 1
    assert session.messages[0].role == MessageRole.ASSISTANT
    assert "Hello" in session.messages[0].content


@pytest.mark.asyncio
async def test_get_session(db_session: AsyncSession, sample_visitor_id: str):
    """Test retrieving a session by ID."""
    service = SessionService(db_session)
    session_create = SessionCreate(visitor_id=sample_visitor_id)

    created = await service.create_session(session_create)
    retrieved = await service.get_session(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.visitor_id == sample_visitor_id


@pytest.mark.asyncio
async def test_get_nonexistent_session(db_session: AsyncSession):
    """Test retrieving a non-existent session returns None."""
    service = SessionService(db_session)
    fake_id = uuid.uuid4()

    result = await service.get_session(fake_id)

    assert result is None


@pytest.mark.asyncio
async def test_add_message(db_session: AsyncSession, sample_visitor_id: str):
    """Test adding a message to a session."""
    service = SessionService(db_session)
    session_create = SessionCreate(visitor_id=sample_visitor_id)
    session = await service.create_session(session_create)

    message_create = MessageCreate(content="Hello, I need help with AI")
    message = await service.add_message(
        session.id, message_create, MessageRole.USER
    )

    assert message.session_id == session.id
    assert message.role == MessageRole.USER
    assert message.content == "Hello, I need help with AI"
    assert message.created_at is not None


@pytest.mark.asyncio
async def test_update_session_activity(db_session: AsyncSession, sample_visitor_id: str):
    """Test updating session activity timestamp."""
    service = SessionService(db_session)
    session_create = SessionCreate(visitor_id=sample_visitor_id)
    session = await service.create_session(session_create)

    original_activity = session.last_activity
    # Small delay to ensure timestamp difference
    import time
    time.sleep(0.001)

    await service.update_session_activity(session)

    assert session.last_activity > original_activity


@pytest.mark.asyncio
async def test_resume_session(db_session: AsyncSession, sample_visitor_id: str):
    """Test resuming a session."""
    service = SessionService(db_session)
    session_create = SessionCreate(visitor_id=sample_visitor_id)
    session = await service.create_session(session_create)

    # Mark as abandoned
    session.status = SessionStatus.ABANDONED
    db_session.add(session)
    await db_session.commit()

    resumed = await service.resume_session(session)

    assert resumed.status == SessionStatus.ACTIVE
    assert resumed.last_activity is not None


@pytest.mark.asyncio
async def test_complete_session(db_session: AsyncSession, sample_visitor_id: str):
    """Test completing a session."""
    service = SessionService(db_session)
    session_create = SessionCreate(visitor_id=sample_visitor_id)
    session = await service.create_session(session_create)

    completed = await service.complete_session(session)

    assert completed.status == SessionStatus.COMPLETED
    assert completed.completed_at is not None


@pytest.mark.asyncio
async def test_update_session_phase(db_session: AsyncSession, sample_visitor_id: str):
    """Test updating session phase."""
    service = SessionService(db_session)
    session_create = SessionCreate(visitor_id=sample_visitor_id)
    session = await service.create_session(session_create)

    await service.update_session_phase(session, SessionPhase.DISCOVERY)

    assert session.current_phase == SessionPhase.DISCOVERY.value


@pytest.mark.asyncio
async def test_update_session_data(db_session: AsyncSession, sample_visitor_id: str):
    """Test updating session data fields."""
    service = SessionService(db_session)
    session_create = SessionCreate(visitor_id=sample_visitor_id)
    session = await service.create_session(session_create)

    # Update client info
    await service.update_session_data(
        session,
        client_info={"name": "John Doe", "email": "john@example.com"},
        business_context={"industry": "Healthcare"},
        qualification={"budget_range": "$50k-100k"},
        lead_score=75,
        recommended_service="AI Strategy",
    )

    assert session.client_info["name"] == "John Doe"
    assert session.client_info["email"] == "john@example.com"
    assert session.business_context["industry"] == "Healthcare"
    assert session.qualification["budget_range"] == "$50k-100k"
    assert session.lead_score == 75
    assert session.recommended_service == "AI Strategy"


@pytest.mark.asyncio
async def test_get_session_messages(db_session: AsyncSession, sample_visitor_id: str):
    """Test retrieving all messages for a session."""
    service = SessionService(db_session)
    session_create = SessionCreate(visitor_id=sample_visitor_id)
    session = await service.create_session(session_create)

    # Add multiple messages
    await service.add_message(
        session.id,
        MessageCreate(content="First message"),
        MessageRole.USER,
    )
    await service.add_message(
        session.id,
        MessageCreate(content="Second message"),
        MessageRole.USER,
    )

    messages = await service.get_session_messages(session.id)

    # Should have 3 messages: 1 welcome + 2 user messages
    assert len(messages) == 3
    assert messages[0].role == MessageRole.ASSISTANT  # Welcome
    assert messages[1].content == "First message"
    assert messages[2].content == "Second message"
