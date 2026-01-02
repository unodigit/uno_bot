"""Integration tests for leads export feature."""
import pytest
from datetime import datetime, timedelta
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.core.database import get_db
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.models.session import ConversationSession, SessionStatus


@pytest.mark.asyncio
async def test_leads_export_json():
    """Test the admin leads export endpoint (JSON format)."""
    # Use in-memory DB
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        from src.core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create test sessions
        # High lead score session (should be included)
        high_lead_session = ConversationSession(
            visitor_id="high-lead-visitor",
            status=SessionStatus.ACTIVE.value,
            started_at=datetime.utcnow() - timedelta(days=2),
            lead_score=85,
            recommended_service="consulting"
        )
        session.add(high_lead_session)

        # Session with booking (should be included)
        booking_session = ConversationSession(
            visitor_id="booking-visitor",
            status=SessionStatus.COMPLETED.value,
            started_at=datetime.utcnow() - timedelta(days=5),
            lead_score=30,  # Low score but has booking
            booking_id="123e4567-e89b-12d3-a456-426614174000"
        )
        session.add(booking_session)

        # Session with PRD (should be included)
        prd_session = ConversationSession(
            visitor_id="prd-visitor",
            status=SessionStatus.COMPLETED.value,
            started_at=datetime.utcnow() - timedelta(days=3),
            lead_score=40,
            prd_id="223e4567-e89b-12d3-a456-426614174000"
        )
        session.add(prd_session)

        # Low lead score session (should NOT be included)
        low_lead_session = ConversationSession(
            visitor_id="low-lead-visitor",
            status=SessionStatus.ACTIVE.value,
            started_at=datetime.utcnow() - timedelta(days=1),
            lead_score=20
        )
        session.add(low_lead_session)

        await session.commit()

        # Override DB dependency
        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # First, create an admin token
            token_response = await client.post(
                "/api/v1/admin/auth/token?username=admin&password=password123"
            )
            assert token_response.status_code == 200
            admin_token = token_response.json()["token"]

            # Test JSON export endpoint
            response = await client.get(
                "/api/v1/admin/export/leads",
                headers={"X-Admin-Token": admin_token}
            )

            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert "leads" in data
            assert "count" in data
            assert "filters" in data

            # Should have 3 leads (high lead, booking, prd)
            assert data["count"] == 3
            assert len(data["leads"]) == 3

            # Verify lead data structure
            lead = data["leads"][0]
            assert "visitor_id" in lead
            assert "session_id" in lead
            assert "lead_score" in lead
            assert "has_booking" in lead
            assert "has_prd" in lead

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_leads_export_csv():
    """Test the admin leads export endpoint (CSV format)."""
    # Use in-memory DB
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        from src.core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create test session
        lead_session = ConversationSession(
            visitor_id="test-visitor",
            status=SessionStatus.ACTIVE.value,
            started_at=datetime.utcnow() - timedelta(days=2),
            lead_score=75,
            recommended_service="strategy",
            booking_id="123e4567-e89b-12d3-a456-426614174000"
        )
        session.add(lead_session)
        await session.commit()

        # Override DB dependency
        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # First, create an admin token
            token_response = await client.post(
                "/api/v1/admin/auth/token?username=admin&password=password123"
            )
            assert token_response.status_code == 200
            admin_token = token_response.json()["token"]

            # Test CSV export endpoint
            response = await client.get(
                "/api/v1/admin/export/leads/csv",
                headers={"X-Admin-Token": admin_token}
            )

            assert response.status_code == 200
            assert "text/csv" in response.headers["content-type"]
            assert "leads_" in response.headers["content-disposition"]

            # Parse CSV content
            csv_content = response.text
            lines = csv_content.strip().split("\n")

            # Should have header + 1 data row
            assert len(lines) == 2

            # Check headers
            header_line = lines[0]
            assert "Visitor ID" in header_line
            assert "Session ID" in header_line
            assert "Lead Score" in header_line
            assert "Has Booking" in header_line

            # Check data row
            data_line = lines[1]
            assert "test-visitor" in data_line
            assert "75" in data_line  # lead score
            assert "Yes" in data_line  # has booking

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_leads_export_with_filters():
    """Test leads export with custom filters."""
    # Use in-memory DB
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        from src.core.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create sessions with different lead scores
        high_score = ConversationSession(
            visitor_id="high",
            status=SessionStatus.ACTIVE.value,
            started_at=datetime.utcnow() - timedelta(days=2),
            lead_score=90
        )
        session.add(high_score)

        medium_score = ConversationSession(
            visitor_id="medium",
            status=SessionStatus.ACTIVE.value,
            started_at=datetime.utcnow() - timedelta(days=2),
            lead_score=60
        )
        session.add(medium_score)

        await session.commit()

        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Get admin token
            token_response = await client.post(
                "/api/v1/admin/auth/token?username=admin&password=password123"
            )
            admin_token = token_response.json()["token"]

            # Test with min_lead_score=70 (should only get high score)
            response = await client.get(
                "/api/v1/admin/export/leads?min_lead_score=70",
                headers={"X-Admin-Token": admin_token}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 1
            assert data["leads"][0]["visitor_id"] == "high"

    app.dependency_overrides.clear()
