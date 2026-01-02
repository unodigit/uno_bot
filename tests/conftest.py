"""Shared test fixtures and configuration."""
import asyncio
from collections.abc import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.database import Base, get_db
from src.core.security import _rate_limit_store
from src.main import app
from src.services.cache_service import cache_service

# Test database URL - uses SQLite for local testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for each test."""
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Clean up all data before test
        from src.models.booking import Booking
        from src.models.expert import Expert
        from src.models.prd import PRDDocument
        from src.models.session import ConversationSession, Message
        from src.models.template import WelcomeMessageTemplate

        await session.execute(Expert.__table__.delete())
        await session.execute(Booking.__table__.delete())
        await session.execute(Message.__table__.delete())
        await session.execute(ConversationSession.__table__.delete())
        await session.execute(PRDDocument.__table__.delete())
        await session.execute(WelcomeMessageTemplate.__table__.delete())
        await session.commit()

        yield session

        # Clean up after test
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override."""
    # Clear rate limiter before each test
    _rate_limit_store.clear()
    # Clear cache before each test
    cache_service.in_memory_cache.cache.clear()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
    # Clear rate limiter after each test
    _rate_limit_store.clear()
    # Clear cache after each test
    cache_service.in_memory_cache.cache.clear()


@pytest.fixture
def sample_visitor_id() -> str:
    """Generate sample visitor ID."""
    return f"visitor_{uuid4().hex[:8]}"


@pytest.fixture
def sample_expert_data() -> dict:
    """Sample expert data for testing."""
    return {
        "name": "John Doe",
        "email": f"john.doe.{uuid4().hex[:6]}@unodigit.com",
        "role": "AI Solutions Architect",
        "bio": "Expert in AI strategy and implementation",
        "specialties": ["AI Strategy", "Machine Learning", "Data Analytics"],
        "services": ["AI Strategy", "Custom Development"],
    }


@pytest.fixture
def sample_session_data(sample_visitor_id: str) -> dict:
    """Sample session data for testing."""
    return {
        "visitor_id": sample_visitor_id,
        "source_url": "https://unodigit.com/services",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0",
    }


@pytest.fixture
def sample_message_data() -> dict:
    """Sample message data for testing."""
    return {
        "content": "Hello, I'm interested in AI solutions for my business.",
        "metadata": {},
    }


@pytest.fixture
def sample_booking_data() -> dict:
    """Sample booking data for testing."""
    from datetime import datetime, timedelta

    return {
        "start_time": (datetime.utcnow() + timedelta(days=2)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(days=2, hours=1)).isoformat(),
        "timezone": "America/New_York",
        "client_name": "Jane Smith",
        "client_email": "jane.smith@example.com",
    }
