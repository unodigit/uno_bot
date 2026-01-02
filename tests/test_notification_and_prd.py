"""Integration tests for notification system and PRD features."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from httpx import ASGITransport, AsyncClient

from src.main import app
from src.core.database import init_db
from src.models.expert import Expert
from src.models.session import ConversationSession, Message
from src.models.prd import PRDDocument
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload


@pytest.mark.asyncio
async def test_email_service_sends_booking_confirmation():
    """Test that EmailService sends booking confirmation email."""
    from src.services.email_service import EmailService

    service = EmailService()

    # Mock the SendGrid API call
    with patch.object(service, '_send_sendgrid_email', return_value=True) as mock_send:
        result = await service.send_booking_confirmation(
            client_email="client@example.com",
            client_name="John Doe",
            expert_name="Jane Smith",
            expert_role="AI Strategy Consultant",
            start_time=datetime.now() + timedelta(days=2),
            end_time=datetime.now() + timedelta(days=2, hours=1),
            timezone="America/New_York",
            meeting_link="https://meet.google.com/abc-defg-hij",
            prd_url="http://example.com/prd/123",
            booking_id="test-booking-id"
        )

        assert result is True
        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_email_service_send_reminder_email():
    """Test that EmailService sends reminder emails."""
    from src.services.email_service import EmailService

    service = EmailService()

    # Mock the SendGrid API call
    with patch.object(service, '_send_sendgrid_email', return_value=True) as mock_send:
        result = await service.send_booking_reminder(
            client_email="client@example.com",
            client_name="John Doe",
            expert_name="Jane Smith",
            expert_role="AI Strategy Consultant",
            start_time=datetime.now() + timedelta(hours=24),
            end_time=datetime.now() + timedelta(hours=25),
            timezone="America/New_York",
            meeting_link="https://meet.google.com/abc-defg-hij",
            reminder_type="24_hours"
        )

        assert result is True
        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_prd_service_generates_conversation_summary():
    """Test that PRDService generates conversation summary."""
    from src.services.prd_service import PRDService
    from src.core.database import get_db

    # Use in-memory database for clean test
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        from src.core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        service = PRDService(session)

        # Create a test session with client info
        session_obj = ConversationSession(
            visitor_id="test-visitor",
            source_url="http://test.com",
            user_agent="test-agent",
            status="active",
            client_info={
                "name": "John Doe",
                "email": "john@example.com",
                "company": "Test Corp"
            },
            business_context={
                "industry": "Technology",
                "challenges": "Need AI integration"
            },
            qualification={
                "budget_range": "$50k-$100k",
                "timeline": "3 months"
            },
            recommended_service="AI Strategy & Planning"
        )

        session.add(session_obj)
        await session.commit()
        await session.refresh(session_obj)

        # Generate summary
        summary = await service.generate_conversation_summary(session_obj)

        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0
        # Check that summary contains key information
        assert "John Doe" in summary or "Test Corp" in summary or "AI Strategy" in summary


@pytest.mark.asyncio
async def test_prd_service_generates_prd_document():
    """Test that PRDService generates PRD document."""
    from src.services.prd_service import PRDService

    # Use in-memory database for clean test
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        from src.core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        service = PRDService(session)

        # Create a test session
        session_obj = ConversationSession(
            visitor_id="test-visitor",
            source_url="http://test.com",
            user_agent="test-agent",
            status="active",
            client_info={
                "name": "John Doe",
                "email": "john@example.com",
                "company": "Test Corp"
            },
            business_context={
                "industry": "Technology",
                "challenges": "Need AI integration",
                "current_tech_stack": "Python, React"
            },
            qualification={
                "budget_range": "$50k-$100k",
                "timeline": "3 months"
            },
            recommended_service="AI Strategy & Planning"
        )

        session.add(session_obj)
        await session.commit()
        await session.refresh(session_obj)

        # Mock AI service to avoid actual LLM calls
        with patch.object(service.ai_service, 'generate_prd', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = """# Project Requirements Document

## Executive Summary
Test Corp needs AI integration strategy.

## Context
Client is a technology company looking to integrate AI solutions.

## Solution
AI Strategy & Planning service to help identify opportunities.

## Parameters
- Budget: $50k-$100k
- Timeline: 3 months
- Tech Stack: Python, React

## Next Steps
Schedule consultation with expert.
"""

            # Generate PRD
            prd = await service.generate_prd(session_obj)

            assert prd is not None
            assert prd.id is not None
            assert prd.session_id == session_obj.id
            assert prd.content_markdown is not None
            assert len(prd.content_markdown) > 0
            assert prd.client_company == "Test Corp"
            assert prd.client_name == "John Doe"
            assert prd.recommended_service == "AI Strategy & Planning"
            assert prd.version == 1
            assert prd.storage_url is not None


@pytest.mark.asyncio
async def test_prd_api_endpoint_creates_prd():
    """Test POST /api/v1/sessions/{id}/prd creates PRD."""
    # Use in-memory database for clean test
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        from src.core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create a test session with full conversation
        session_obj = ConversationSession(
            visitor_id="test-visitor",
            source_url="http://test.com",
            user_agent="test-agent",
            status="active",
            client_info={
                "name": "Jane Doe",
                "email": "jane@example.com",
                "company": "Acme Corp"
            },
            business_context={
                "industry": "E-commerce",
                "challenges": "Need custom development"
            },
            qualification={
                "budget_range": "$100k+",
                "timeline": "6 months"
            },
            recommended_service="Custom Development"
        )

        session.add(session_obj)
        await session.commit()
        await session.refresh(session_obj)

        # Override DB dependency
        from src.core.database import get_db
        async def override_get_db():
            yield session
        app.dependency_overrides[get_db] = override_get_db

        # Mock AI service
        with patch('src.services.prd_service.AIService') as mock_ai_service:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = Mock(content="Conversation summary here")
            mock_ai_service.return_value.llm = mock_llm
            mock_ai_service.return_value.generate_prd = AsyncMock(return_value="# Test PRD\n\nContent here")

            # Test API endpoint
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(f"/api/v1/sessions/{session_obj.id}/prd")

                assert response.status_code == 201
                data = response.json()
                assert data["id"] is not None
                assert data["content_markdown"] is not None
                assert data["client_company"] == "Acme Corp"

    # Clean up
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_prd_download_endpoint_works():
    """Test GET /api/v1/prd/{id}/download returns PRD file."""
    # Use in-memory database for clean test
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        from src.core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create a test PRD
        session_obj = ConversationSession(
            visitor_id="test-visitor",
            source_url="http://test.com",
            user_agent="test-agent",
            status="completed",
            client_info={"name": "Test User", "company": "Test Company"}
        )
        session.add(session_obj)
        await session.commit()
        await session.refresh(session_obj)

        prd = PRDDocument(
            session_id=session_obj.id,
            content_markdown="# Test PRD\n\nThis is test content.",
            conversation_summary="Summary here",
            client_company="Test Company",
            client_name="Test User",
            recommended_service="AI Strategy",
            version=1
        )
        session.add(prd)
        await session.commit()
        await session.refresh(prd)

        # Override DB dependency
        from src.core.database import get_db
        async def override_get_db():
            yield session
        app.dependency_overrides[get_db] = override_get_db

        # Test API endpoint
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/prd/{prd.id}/download")

            assert response.status_code == 200
            assert response.headers["content-type"] == "text/markdown; charset=utf-8"
            content = response.text
            assert "Test PRD" in content
            assert "test content" in content

    # Clean up
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_prd_preview_endpoint_works():
    """Test GET /api/v1/prd/{id}/preview returns PRD preview."""
    # Use in-memory database for clean test
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        from src.core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create test PRD
        session_obj = ConversationSession(
            visitor_id="test-visitor",
            source_url="http://test.com",
            user_agent="test-agent",
            status="completed",
            client_info={"name": "Test User", "company": "Test Company"}
        )
        session.add(session_obj)
        await session.commit()

        prd = PRDDocument(
            session_id=session_obj.id,
            content_markdown="# Test PRD\n\nThis is test content.",
            conversation_summary="Summary here",
            client_company="Test Company",
            client_name="Test User",
            recommended_service="AI Strategy",
            version=1
        )
        session.add(prd)
        await session.commit()
        await session.refresh(prd)

        # Override DB dependency
        from src.core.database import get_db
        async def override_get_db():
            yield session
        app.dependency_overrides[get_db] = override_get_db

        # Test API endpoint
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/prd/{prd.id}/preview")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(prd.id)
            assert data["content_markdown"] is not None
            assert data["client_company"] == "Test Company"

    # Clean up
    app.dependency_overrides.clear()
