"""Integration tests for conversation summary feature."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.prd import PRDDocument
from src.models.session import ConversationSession, Message
from src.schemas.session import SessionCreate
from src.services.prd_service import PRDService
from src.services.session_service import SessionService


@pytest.mark.asyncio
async def test_generate_conversation_summary(db_session: AsyncSession):
    """Test generating a conversation summary."""
    # Create a test session
    session_service = SessionService(db_session)
    session_create = SessionCreate(
        visitor_id="test_visitor_summary",
        source_url="http://test.com",
        user_agent="test-agent"
    )
    session = await session_service.create_session(session_create)

    # Add some messages to simulate conversation
    messages = [
        Message(
            session_id=session.id,
            role="user",
            content="Hi, I'm John from Acme Corp. We need help with our e-commerce platform.",
            meta_data={}
        ),
        Message(
            session_id=session.id,
            role="assistant",
            content="Hello John! What challenges are you facing with your e-commerce platform?",
            meta_data={}
        ),
        Message(
            session_id=session.id,
            role="user",
            content="We're seeing slow performance during peak hours and need better inventory management. Budget is around $50k, timeline is 2 months.",
            meta_data={}
        ),
    ]
    for msg in messages:
        db_session.add(msg)
    await db_session.commit()

    # Reload session and update with business context
    result = await db_session.execute(
        select(ConversationSession)
        .options(selectinload(ConversationSession.messages))
        .where(ConversationSession.id == session.id)
    )
    session = result.scalar_one()

    session.client_info = {"name": "John", "company": "Acme Corp"}
    session.business_context = {
        "industry": "E-commerce",
        "challenges": "Slow performance during peak hours, need better inventory management"
    }
    session.qualification = {"budget_range": "$50k", "timeline": "2 months"}
    session.recommended_service = "E-commerce Platform Optimization"
    db_session.add(session)
    await db_session.commit()

    # Generate summary
    prd_service = PRDService(db_session)
    summary = await prd_service.generate_conversation_summary(session)

    # Verify summary was generated
    assert summary is not None
    assert len(summary) > 0
    # Summary should contain relevant context
    assert "Acme Corp" in summary or "John" in summary


@pytest.mark.asyncio
async def test_generate_prd_with_summary(db_session: AsyncSession):
    """Test generating PRD with conversation summary."""
    # Create a test session
    session_service = SessionService(db_session)
    session_create = SessionCreate(
        visitor_id="test_visitor_prd",
        source_url="http://test.com",
        user_agent="test-agent"
    )
    session = await session_service.create_session(session_create)

    # Add messages
    message = Message(
        session_id=session.id,
        role="user",
        content="We need a mobile app for our logistics company.",
        meta_data={}
    )
    db_session.add(message)
    await db_session.commit()

    # Reload and update session
    result = await db_session.execute(
        select(ConversationSession)
        .where(ConversationSession.id == session.id)
    )
    session = result.scalar_one()

    session.client_info = {"name": "Alice", "company": "Logistics Inc"}
    session.business_context = {"industry": "Logistics", "challenges": "Need mobile app"}
    session.qualification = {"budget_range": "$100k", "timeline": "3 months"}
    session.recommended_service = "Mobile App Development"
    db_session.add(session)
    await db_session.commit()

    # Generate summary first
    prd_service = PRDService(db_session)
    summary = await prd_service.generate_conversation_summary(session)

    # Generate PRD with summary
    prd = await prd_service.generate_prd(session, summary)

    # Verify PRD was created with summary
    assert prd is not None
    assert prd.conversation_summary is not None
    assert prd.conversation_summary == summary
    assert prd.session_id == session.id


@pytest.mark.asyncio
async def test_regenerate_prd_preserves_summary(db_session: AsyncSession):
    """Test that regenerating PRD preserves the conversation summary."""
    # Create a test session
    session_service = SessionService(db_session)
    session_create = SessionCreate(
        visitor_id="test_visitor_regen",
        source_url="http://test.com",
        user_agent="test-agent"
    )
    session = await session_service.create_session(session_create)

    # Add messages
    message = Message(
        session_id=session.id,
        role="user",
        content="We need a CRM system.",
        meta_data={}
    )
    db_session.add(message)
    await db_session.commit()

    # Reload and update session
    result = await db_session.execute(
        select(ConversationSession)
        .where(ConversationSession.id == session.id)
    )
    session = result.scalar_one()

    session.client_info = {"name": "Bob", "company": "SalesCo"}
    session.business_context = {"industry": "Sales", "challenges": "Need CRM"}
    session.qualification = {"budget_range": "$75k", "timeline": "4 months"}
    session.recommended_service = "CRM Development"
    db_session.add(session)
    await db_session.commit()

    # Generate PRD with summary
    prd_service = PRDService(db_session)
    summary = await prd_service.generate_conversation_summary(session)
    prd = await prd_service.generate_prd(session, summary)

    # Regenerate PRD
    new_prd = await prd_service.regenerate_prd(session, "Make it more detailed")

    # Verify new PRD has same summary
    assert new_prd.conversation_summary == summary
    assert new_prd.version == 2


@pytest.mark.asyncio
async def test_summary_in_prd_model(db_session: AsyncSession):
    """Test that PRD model stores conversation summary."""
    # Create a test session
    session_service = SessionService(db_session)
    session_create = SessionCreate(
        visitor_id="test_visitor_model",
        source_url="http://test.com",
        user_agent="test-agent"
    )
    session = await session_service.create_session(session_create)

    # Update session
    result = await db_session.execute(
        select(ConversationSession).where(ConversationSession.id == session.id)
    )
    session = result.scalar_one()

    session.client_info = {"name": "Charlie", "company": "TechCorp"}
    session.business_context = {"industry": "Tech", "challenges": "Need platform"}
    session.qualification = {"budget_range": "$60k", "timeline": "3 months"}
    session.recommended_service = "Platform Development"
    db_session.add(session)
    await db_session.commit()

    # Generate PRD with summary
    prd_service = PRDService(db_session)
    summary = "Test summary for TechCorp - need platform development"
    prd = await prd_service.generate_prd(session, summary)

    # Verify in database
    result = await db_session.execute(
        select(PRDDocument).where(PRDDocument.id == prd.id)
    )
    db_prd = result.scalar_one()

    assert db_prd.conversation_summary == summary


@pytest.mark.asyncio
async def test_fallback_summary_when_ai_unavailable(db_session: AsyncSession):
    """Test that fallback summary works when AI service is unavailable."""
    # Create a test session
    session_service = SessionService(db_session)
    session_create = SessionCreate(
        visitor_id="test_visitor_fallback",
        source_url="http://test.com",
        user_agent="test-agent"
    )
    session = await session_service.create_session(session_create)

    # Update session
    result = await db_session.execute(
        select(ConversationSession).where(ConversationSession.id == session.id)
    )
    session = result.scalar_one()

    session.client_info = {"name": "Diana", "company": "DesignHub"}
    session.business_context = {"industry": "Design", "challenges": "Need platform"}
    session.qualification = {"budget_range": "$50k", "timeline": "2 months"}
    session.recommended_service = "Platform Development"
    db_session.add(session)
    await db_session.commit()

    # Generate summary (will use fallback since no LLM is configured)
    prd_service = PRDService(db_session)
    summary = await prd_service.generate_conversation_summary(session)

    # Verify fallback summary was created
    assert summary is not None
    assert len(summary) > 0
    assert "Diana" in summary or "DesignHub" in summary
