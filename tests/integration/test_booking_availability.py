"""Integration tests for booking availability and creation functionality."""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.expert import Expert
from src.models.session import ConversationSession
from src.models.booking import Booking


@pytest.mark.asyncio
async def test_get_expert_availability_returns_slots(db_session: AsyncSession, client: AsyncClient):
    """Test that availability endpoint returns at least 5 slots over 14 days.

    Feature: At least 5 available slots shown over 14 days
    """
    # Create an expert with unique email
    unique_id = uuid4().hex[:8]
    expert = Expert(
        name=f"Test Expert {unique_id}",
        email=f"expert_{unique_id}@test.com",
        role="Consultant",
        specialties=["AI Strategy"],
        services=["AI Strategy & Planning"],
        is_active=True,
    )
    db_session.add(expert)
    await db_session.commit()
    await db_session.refresh(expert)

    # Get availability
    response = await client.get(f"/api/v1/bookings/experts/{expert.id}/availability")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "slots" in data
    assert "expert_id" in data
    assert "expert_name" in data
    assert "timezone" in data

    # Verify at least 5 slots are returned
    slots = data["slots"]
    assert len(slots) >= 5, f"Expected at least 5 slots, got {len(slots)}"

    # Verify slots span up to 14 days
    if len(slots) > 0:
        start_time = datetime.fromisoformat(slots[0]["start_time"])
        end_time = datetime.fromisoformat(slots[-1]["start_time"])
        days_span = (end_time - start_time).days
        assert days_span <= 14, f"Slots should span up to 14 days, got {days_span} days"

    # Verify slots are within business hours (9-17)
    for slot in slots:
        slot_time = datetime.fromisoformat(slot["start_time"])
        hour = slot_time.hour
        assert 9 <= hour <= 17, f"Slot at {hour}:00 is outside business hours (9-17)"


@pytest.mark.asyncio
async def test_get_expert_availability_with_custom_parameters(db_session: AsyncSession, client: AsyncClient):
    """Test availability with custom days_ahead and min_slots_to_show parameters."""
    unique_id = uuid4().hex[:8]
    expert = Expert(
        name=f"Test Expert {unique_id}",
        email=f"expert_{unique_id}@test.com",
        role="Consultant",
        specialties=["AI Strategy"],
        services=["AI Strategy & Planning"],
        is_active=True,
    )
    db_session.add(expert)
    await db_session.commit()
    await db_session.refresh(expert)

    # Test with custom parameters
    response = await client.get(
        f"/api/v1/bookings/experts/{expert.id}/availability",
        params={"days_ahead": 7, "min_slots_to_show": 3}
    )

    assert response.status_code == 200
    data = response.json()
    slots = data["slots"]

    # Should have at least 3 slots
    assert len(slots) >= 3

    # Slots should be within 7 days
    if len(slots) > 0:
        start_time = datetime.fromisoformat(slots[0]["start_time"])
        end_time = datetime.fromisoformat(slots[-1]["start_time"])
        days_span = (end_time - start_time).days
        assert days_span <= 7


@pytest.mark.asyncio
async def test_get_expert_availability_404_for_nonexistent_expert(client: AsyncClient):
    """Test that availability returns 404 for non-existent expert."""
    fake_id = uuid4()

    response = await client.get(f"/api/v1/bookings/experts/{fake_id}/availability")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_booking_creates_calendar_event(db_session: AsyncSession, client: AsyncClient):
    """Test that booking creation creates a calendar event.

    Feature: Booking creation creates calendar event
    """
    # Create expert
    unique_id = uuid4().hex[:8]
    expert = Expert(
        name=f"Test Expert {unique_id}",
        email=f"expert_{unique_id}@test.com",
        role="Consultant",
        specialties=["AI Strategy"],
        services=["AI Strategy & Planning"],
        is_active=True,
    )
    db_session.add(expert)
    await db_session.commit()
    await db_session.refresh(expert)

    # Create session
    session = ConversationSession(
        visitor_id=f"test_visitor_{unique_id}",
        source_url="http://test.com",
        user_agent="test",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Create booking
    now = datetime.utcnow()
    booking_data = {
        "expert_id": str(expert.id),
        "start_time": (now + timedelta(days=2)).isoformat(),
        "end_time": (now + timedelta(days=2, hours=1)).isoformat(),
        "client_name": "Test Client",
        "client_email": f"client_{unique_id}@test.com",
    }

    response = await client.post(
        f"/api/v1/bookings/sessions/{session.id}/bookings",
        json=booking_data
    )

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    booking = response.json()

    # Verify booking was created
    assert "id" in booking
    assert booking["client_name"] == "Test Client"
    assert booking["client_email"] == f"client_{unique_id}@test.com"
    assert booking["expert_id"] == str(expert.id)

    # Verify calendar event was created (mock returns a string)
    assert "calendar_event_id" in booking
    assert booking["calendar_event_id"] is not None
    assert booking["calendar_event_id"].startswith("mock-event-")

    # Verify meeting link is generated (mock creates a Google Meet link)
    assert "meeting_link" in booking
    assert booking["meeting_link"] is not None
    assert "meet.google.com" in booking["meeting_link"]


@pytest.mark.asyncio
async def test_create_booking_stores_in_database(db_session: AsyncSession, client: AsyncClient):
    """Test that created booking is stored in database."""
    # Create expert
    unique_id = uuid4().hex[:8]
    expert = Expert(
        name=f"Test Expert {unique_id}",
        email=f"expert_{unique_id}@test.com",
        role="Consultant",
        specialties=["AI Strategy"],
        services=["AI Strategy & Planning"],
        is_active=True,
    )
    db_session.add(expert)
    await db_session.commit()
    await db_session.refresh(expert)

    # Create session
    session = ConversationSession(
        visitor_id=f"test_visitor_{unique_id}",
        source_url="http://test.com",
        user_agent="test",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Create booking
    now = datetime.utcnow()
    client_email = f"jane_{unique_id}@example.com"
    booking_data = {
        "expert_id": str(expert.id),
        "start_time": (now + timedelta(days=3)).isoformat(),
        "end_time": (now + timedelta(days=3, hours=1)).isoformat(),
        "client_name": "Jane Doe",
        "client_email": client_email,
    }

    response = await client.post(
        f"/api/v1/bookings/sessions/{session.id}/bookings",
        json=booking_data
    )

    assert response.status_code == 201

    # Verify booking exists in database
    result = await db_session.execute(
        select(Booking).where(Booking.client_email == client_email)
    )
    booking = result.scalar_one_or_none()

    assert booking is not None
    assert booking.client_name == "Jane Doe"
    assert booking.expert_id == expert.id
    assert booking.session_id == session.id


@pytest.mark.asyncio
async def test_booking_has_correct_time_and_timezone(db_session: AsyncSession, client: AsyncClient):
    """Test that booking has correct time and timezone."""
    # Create expert
    unique_id = uuid4().hex[:8]
    expert = Expert(
        name=f"Test Expert {unique_id}",
        email=f"expert_{unique_id}@test.com",
        role="Consultant",
        specialties=["AI Strategy"],
        services=["AI Strategy & Planning"],
        is_active=True,
    )
    db_session.add(expert)
    await db_session.commit()
    await db_session.refresh(expert)

    # Create session
    session = ConversationSession(
        visitor_id=f"test_visitor_{unique_id}",
        source_url="http://test.com",
        user_agent="test",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Create booking with specific timezone
    # Use specific times to make testing predictable
    start_time = datetime(2026, 1, 10, 14, 30, 0)  # 2:30 PM
    end_time = datetime(2026, 1, 10, 15, 30, 0)    # 3:30 PM

    booking_data = {
        "expert_id": str(expert.id),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "timezone": "America/New_York",
        "client_name": "Test Client",
        "client_email": f"client_{unique_id}@test.com",
    }

    response = await client.post(
        f"/api/v1/bookings/sessions/{session.id}/bookings",
        json=booking_data
    )

    assert response.status_code == 201
    booking = response.json()

    # Verify times are preserved correctly
    returned_start = datetime.fromisoformat(booking["start_time"])
    returned_end = datetime.fromisoformat(booking["end_time"])

    assert returned_start.year == 2026
    assert returned_start.month == 1
    assert returned_start.day == 10
    assert returned_start.hour == 14
    assert returned_start.minute == 30
    assert (returned_end - returned_start).total_seconds() == 3600  # 1 hour

    # Verify timezone is stored
    assert booking["timezone"] == "America/New_York"
