"""Integration tests for Google Calendar OAuth functionality."""
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import decrypt_oauth_token
from src.schemas.expert import ExpertCreate
from src.services.expert_service import ExpertService


@pytest.mark.asyncio
async def test_google_calendar_oauth_flow_completes_successfully(
    client: AsyncClient, db_session: AsyncSession
):
    """Test that Google Calendar OAuth flow completes successfully.

    Feature: Google Calendar OAuth flow completes successfully

    This test simulates the complete OAuth flow:
    1. Create an expert
    2. Initiate OAuth flow to get authorization URL
    3. Simulate callback with mock credentials
    4. Verify refresh_token and calendar_id are stored
    """
    service = ExpertService(db_session)

    # Step 1: Create an expert
    expert = await service.create_expert(
        ExpertCreate(
            name="Test Expert",
            email=f"expert.{uuid.uuid4().hex[:6]}@example.com",
            role="AI Consultant",
            bio="Expert in AI",
            specialties=["AI"],
            services=["AI Strategy & Planning"],
            is_active=True,
        )
    )

    # Step 2: Initiate OAuth flow
    response = await client.post(f"/api/v1/experts/{expert.id}/connect_calendar")
    assert response.status_code == 200
    oauth_data = response.json()

    # Verify OAuth URL is returned
    assert oauth_data["success"] is True
    assert "message" in oauth_data
    assert oauth_data["message"].startswith("https://") or oauth_data["message"] == "https://test-oauth.example.com/auth"

    # Step 3: Simulate OAuth callback
    # In test environment, the mock flow will accept any code
    callback_response = await client.get(
        "/api/v1/experts/calendar/callback",
        params={"code": "test_auth_code", "expert_id": str(expert.id)}
    )
    assert callback_response.status_code == 200
    callback_data = callback_response.json()

    # Verify callback success
    assert callback_data["success"] is True
    assert callback_data["calendar_id"] is not None
    assert "Calendar connected successfully" in callback_data["message"]

    # Step 4: Verify expert has refresh_token and calendar_id stored
    # Use get_expert_model to access sensitive fields like refresh_token
    updated_expert = await service.get_expert_model(expert.id)
    # Refresh token is now encrypted in the database
    decrypted_token = decrypt_oauth_token(updated_expert.refresh_token)
    assert decrypted_token == "test_refresh_token"
    assert updated_expert.calendar_id is not None


@pytest.mark.asyncio
async def test_oauth_callback_validates_code_required(
    client: AsyncClient, db_session: AsyncSession
):
    """Test that OAuth callback requires authorization code.

    Note: FastAPI returns 422 (Unprocessable Entity) for missing required
    query parameters, which is the expected behavior.
    """
    service = ExpertService(db_session)

    # Create expert
    expert = await service.create_expert(
        ExpertCreate(
            name="Test Expert",
            email=f"expert.{uuid.uuid4().hex[:6]}@example.com",
            role="AI Consultant",
            bio="Expert in AI",
            specialties=["AI"],
            services=["AI Strategy & Planning"],
            is_active=True,
        )
    )

    # Try callback without code - FastAPI returns 422 for missing required param
    response = await client.get(
        "/api/v1/experts/calendar/callback",
        params={"expert_id": str(expert.id)}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_oauth_callback_validates_expert_exists(
    client: AsyncClient
):
    """Test that OAuth callback handles non-existent expert.

    The endpoint should return 404 when the expert doesn't exist.
    """
    fake_id = uuid.uuid4()

    # Try callback with non-existent expert
    response = await client.get(
        "/api/v1/experts/calendar/callback",
        params={"code": "test_code", "expert_id": str(fake_id)}
    )
    # The endpoint returns 404 for non-existent expert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_calendar_availability_fetches_from_mock(
    client: AsyncClient, db_session: AsyncSession
):
    """Test that calendar availability fetches from mock service.

    Feature: Calendar availability fetches from Google Calendar API

    Note: In test environment, this uses MockCalendarService
    """
    from src.models.expert import Expert

    # Create expert with refresh token (simulating connected calendar)
    expert = Expert(
        name="Test Expert",
        email=f"expert.{uuid.uuid4().hex[:6]}@example.com",
        role="AI Consultant",
        specialties=["AI"],
        services=["AI Strategy & Planning"],
        is_active=True,
        refresh_token="test_refresh_token",  # Simulates connected calendar
    )
    db_session.add(expert)
    await db_session.commit()
    await db_session.refresh(expert)

    # Get availability
    response = await client.get(f"/api/v1/bookings/experts/{expert.id}/availability")
    assert response.status_code == 200

    data = response.json()
    assert "slots" in data
    assert len(data["slots"]) >= 5  # At least 5 slots

    # Verify slot structure
    for slot in data["slots"]:
        assert "start_time" in slot
        assert "end_time" in slot
        assert "display_time" in slot
        assert "display_date" in slot


@pytest.mark.asyncio
async def test_calendar_availability_with_custom_parameters(
    client: AsyncClient, db_session: AsyncSession
):
    """Test calendar availability with custom parameters."""
    from src.models.expert import Expert

    # Create expert
    expert = Expert(
        name="Test Expert",
        email=f"expert.{uuid.uuid4().hex[:6]}@example.com",
        role="AI Consultant",
        specialties=["AI"],
        services=["AI Strategy & Planning"],
        is_active=True,
        refresh_token="test_refresh_token",
    )
    db_session.add(expert)
    await db_session.commit()
    await db_session.refresh(expert)

    # Get availability with custom parameters
    response = await client.get(
        f"/api/v1/bookings/experts/{expert.id}/availability",
        params={"days_ahead": 7, "min_slots_to_show": 10}
    )
    assert response.status_code == 200

    data = response.json()
    slots = data["slots"]

    # Should have at least 10 slots
    assert len(slots) >= 10

    # All slots should be within 7 days
    if len(slots) > 0:
        from datetime import datetime
        start_time = datetime.fromisoformat(slots[0]["start_time"])
        end_time = datetime.fromisoformat(slots[-1]["start_time"])
        days_span = (end_time - start_time).days
        assert days_span <= 7
