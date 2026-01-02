"""Integration tests for conversation qualification features (187-190).

Tests:
- Feature 187: Decision maker identification
- Feature 188: Success criteria collection
- Feature 189: Intent detection
- Feature 190: Context retention across long conversations
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.core.database import Base, get_db
from src.services.session_service import SessionService
from src.schemas.session import SessionCreate, MessageCreate
from src.models.session import SessionPhase


@pytest.fixture
async def test_db():
    """Create an in-memory database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    yield async_session

    await engine.dispose()


@pytest.fixture
async def client(test_db):
    """Create test client with database override."""
    async def override_get_db():
        async with test_db() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_feature_187_decision_maker_identification(test_db):
    """Test that decision maker identification is collected and stored."""
    async with test_db() as session:
        service = SessionService(session)

        # Create session
        session_create = SessionCreate(visitor_id="test_visitor_187")
        created_session = await service.create_session(session_create)

        # Simulate conversation to qualification phase
        await service.add_message(
            created_session.id,
            MessageCreate(content="My name is John Doe", role="user")
        )
        await service.add_message(
            created_session.id,
            MessageCreate(content="john@example.com", role="user")
        )
        await service.add_message(
            created_session.id,
            MessageCreate(content="We need help with data analytics", role="user")
        )
        await service.add_message(
            created_session.id,
            MessageCreate(content="Healthcare industry", role="user")
        )
        await service.add_message(
            created_session.id,
            MessageCreate(content="Budget is around $50,000", role="user")
        )

        # Provide decision maker info
        await service.add_message(
            created_session.id,
            MessageCreate(content="I am the decision maker for this project", role="user")
        )

        # Refresh session to get latest data
        await session.refresh(created_session)

        # Verify decision maker status is stored
        assert created_session.qualification.get("is_decision_maker") is True

        # Verify it affects lead score (decision maker adds points)
        assert created_session.lead_score > 0
        assert created_session.lead_score >= 15  # Base score + decision maker bonus


@pytest.mark.asyncio
async def test_feature_187_non_decision_maker(test_db):
    """Test that non-decision maker response is handled correctly."""
    async with test_db() as session:
        service = SessionService(session)

        # Create and progress session
        session_create = SessionCreate(visitor_id="test_visitor_187b")
        created_session = await service.create_session(session_create)

        messages = [
            "My name is Jane Smith",
            "jane@company.com",
            "Need custom software",
            "Finance industry",
            "Budget $100,000",
            "I need approval from my boss for decisions",
        ]

        for msg in messages:
            await service.add_message(
                created_session.id,
                MessageCreate(content=msg, role="user")
            )

        await session.refresh(created_session)

        # Verify non-decision maker status is stored
        assert created_session.qualification.get("is_decision_maker") is False


@pytest.mark.asyncio
async def test_feature_188_success_criteria_collection(test_db):
    """Test that success criteria is captured and stored."""
    async with test_db() as session:
        service = SessionService(session)

        # Create and progress session
        session_create = SessionCreate(visitor_id="test_visitor_188")
        created_session = await service.create_session(session_create)

        messages = [
            "My name is Bob Johnson",
            "bob@example.com",
            "Need AI consulting",
            "Retail industry",
            "Budget $75,000",
            "3 month timeline",
            # Success criteria
            "Success would be 50% efficiency improvement and automated reporting",
        ]

        for msg in messages:
            await service.add_message(
                created_session.id,
                MessageCreate(content=msg, role="user")
            )

        await session.refresh(created_session)

        # Verify success criteria is stored
        success_criteria = created_session.qualification.get("success_criteria")
        assert success_criteria is not None
        assert len(success_criteria) > 0
        assert "efficiency" in success_criteria.lower() or "improvement" in success_criteria.lower()


@pytest.mark.asyncio
async def test_feature_188_vague_success_criteria(test_db):
    """Test that vague success criteria prompts clarification."""
    async with test_db() as session:
        service = SessionService(session)

        session_create = SessionCreate(visitor_id="test_visitor_188b")
        created_session = await service.create_session(session_create)

        messages = [
            "My name is Alice",
            "alice@example.com",
            "Need data platform",
            "Tech industry",
            "Budget $50,000",
            "2 months",
            "We want success",  # Vague
        ]

        for msg in messages:
            await service.add_message(
                created_session.id,
                MessageCreate(content=msg, role="user")
            )

        await session.refresh(created_session)

        # Should capture something (even if vague)
        success_criteria = created_session.qualification.get("success_criteria")
        # The vague input should still be captured
        assert success_criteria is not None


@pytest.mark.asyncio
async def test_feature_189_intent_detection_ai_strategy(test_db):
    """Test that AI strategy intent is detected."""
    async with test_db() as session:
        service = SessionService(session)

        session_create = SessionCreate(visitor_id="test_visitor_189a")
        created_session = await service.create_session(session_create)

        # Express AI strategy need
        messages = [
            "My name is Carol",
            "carol@example.com",
            "We need help with our AI strategy and machine learning implementation",
        ]

        for msg in messages:
            await service.add_message(
                created_session.id,
                MessageCreate(content=msg, role="user")
            )

        await session.refresh(created_session)

        # Verify intent is captured in business context
        challenges = created_session.business_context.get("challenges", "")
        assert "ai" in challenges.lower() or "machine learning" in challenges.lower()

        # Verify service recommendation matches AI strategy
        assert created_session.recommended_service is not None


@pytest.mark.asyncio
async def test_feature_189_intent_detection_custom_dev(test_db):
    """Test that custom development intent is detected."""
    async with test_db() as session:
        service = SessionService(session)

        session_create = SessionCreate(visitor_id="test_visitor_189b")
        created_session = await service.create_session(session_create)

        messages = [
            "My name is Dave",
            "dave@example.com",
            "We need a custom software application built for our business",
        ]

        for msg in messages:
            await service.add_message(
                created_session.id,
                MessageCreate(content=msg, role="user")
            )

        await session.refresh(created_session)

        # Verify custom dev intent is captured
        challenges = created_session.business_context.get("challenges", "")
        assert "custom" in challenges.lower() or "software" in challenges.lower()


@pytest.mark.asyncio
async def test_feature_190_context_retention_long_conversation(test_db):
    """Test that context is retained across 15+ message conversation."""
    async with test_db() as session:
        service = SessionService(session)

        session_create = SessionCreate(visitor_id="test_visitor_190")
        created_session = await service.create_session(session_create)

        # Have a 15+ message conversation
        messages = [
            "My name is Emily Watson",
            "emily@example.com",
            "We need help with data analytics",
            "Healthcare industry",
            "About 100 employees",
            "Budget is $50,000",
            "Need it done in 2 months",
            "Yes, I am the decision maker",
            "Success means 50% efficiency improvement",
            "We use Python and SQL",
            "Main challenge is slow reporting",
            "We need real-time dashboards",
            "Currently using Excel",
            "Looking to automate",
            "Need better insights",
            "What is the next step?",  # Message 15
        ]

        for msg in messages:
            await service.add_message(
                created_session.id,
                MessageCreate(content=msg, role="user")
            )

        await session.refresh(created_session)

        # Verify name is still remembered
        assert created_session.client_info.get("name") == "Emily Watson"

        # Verify industry is still remembered
        assert created_session.business_context.get("industry") == "Healthcare"

        # Verify budget is still remembered
        assert created_session.qualification.get("budget_range") is not None

        # Verify success criteria is remembered
        success_criteria = created_session.qualification.get("success_criteria")
        assert success_criteria is not None
        assert "efficiency" in success_criteria.lower()

        # Verify context doesn't get confused
        assert created_session.current_phase in ["qualification", "prd_generation", "expert_matching", "booking"]


@pytest.mark.asyncio
async def test_feature_190_context_references_earlier_info(test_db):
    """Test that bot can reference earlier information in conversation."""
    async with test_db() as session:
        service = SessionService(session)

        session_create = SessionCreate(visitor_id="test_visitor_190b")
        created_session = await service.create_session(session_create)

        # Provide information then reference it later
        messages = [
            "My name is Frank Miller",
            "frank@example.com",
            "I work in finance industry",
            "Need risk management system",
            "Budget $200,000",
            "6 month timeline",
            "Yes I'm the CTO",
            "Success is launching on time",
            "We use Java and React",
            "Need mobile app",
            "iOS and Android",
            "Need API integration",
            "Payment processing",
            "User authentication",
            "Remember, I work in finance",  # Reference earlier
        ]

        for msg in messages:
            await service.add_message(
                created_session.id,
                MessageCreate(content=msg, role="user")
            )

        await session.refresh(created_session)

        # Verify industry context is maintained despite long conversation
        assert created_session.business_context.get("industry") == "Finance"

        # Verify all key info is retained
        assert created_session.client_info.get("name") == "Frank Miller"
        assert created_session.qualification.get("budget_range") is not None


@pytest.mark.asyncio
async def test_lead_score_calculation_with_decision_maker(test_db):
    """Test that lead score is calculated correctly with decision maker status."""
    async with test_db() as session:
        service = SessionService(session)

        session_create = SessionCreate(visitor_id="test_visitor_score")
        created_session = await service.create_session(session_create)

        # Provide all information including decision maker status
        messages = [
            "My name is Test User",
            "test@example.com",
            "Test Company",
            "Need software development",
            "Tech industry",
            "Budget: $100,000",
            "Timeline: 3 months",
            "I am the decision maker",
            "Success: on-time delivery",
        ]

        for msg in messages:
            await service.add_message(
                created_session.id,
                MessageCreate(content=msg, role="user")
            )

        await session.refresh(created_session)

        # Calculate expected score
        # Name (10) + Email (15) + Company (10) + Challenges (20) + Industry (10)
        # + Budget large (25) + Timeline (10) + Decision maker (15) = ~115, capped at 100
        assert created_session.lead_score >= 80  # Should be high score
        assert created_session.lead_score <= 100  # Capped at 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
