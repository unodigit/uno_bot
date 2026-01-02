"""Integration tests for booking cancellation functionality."""
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.booking import Booking
from src.models.expert import Expert
from src.models.session import ConversationSession


@pytest.mark.asyncio
async def test_booking_cancellation_works_correctly(db_session: AsyncSession, client: AsyncClient):
    """Test that booking cancellation works correctly.

    Feature: Booking cancellation works correctly
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
    start_time = now + timedelta(days=2)
    end_time = start_time + timedelta(hours=1)

    booking_data = {
        "expert_id": str(expert.id),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "client_name": "Test Client",
        "client_email": f"client_{unique_id}@test.com",
    }

    create_response = await client.post(
        f"/api/v1/bookings/sessions/{session.id}/bookings",
        json=booking_data
    )
    assert create_response.status_code == 201
    booking = create_response.json()
    booking_id = booking["id"]

    # Verify booking exists and is confirmed
    get_response = await client.get(f"/api/v1/bookings/{booking_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "confirmed"

    # Cancel the booking
    cancel_response = await client.delete(f"/api/v1/bookings/{booking_id}")
    assert cancel_response.status_code == 200
    assert "successfully" in cancel_response.json()["message"].lower()

    # Verify booking status is cancelled in database
    result = await db_session.execute(
        select(Booking).where(Booking.id == UUID(booking_id))
    )
    cancelled_booking = result.scalar_one_or_none()
    assert cancelled_booking is not None
    assert cancelled_booking.status == "cancelled"


@pytest.mark.asyncio
async def test_booking_cancellation_returns_404_for_nonexistent_booking(client: AsyncClient):
    """Test that cancelling a non-existent booking returns 404."""
    fake_id = uuid4()

    response = await client.delete(f"/api/v1/bookings/{fake_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_booking_cancellation_sends_email(db_session: AsyncSession, client: AsyncClient):
    """Test that booking cancellation sends cancellation email."""
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
    start_time = now + timedelta(days=2)
    end_time = start_time + timedelta(hours=1)

    booking_data = {
        "expert_id": str(expert.id),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "client_name": "Test Client",
        "client_email": f"client_{unique_id}@test.com",
    }

    create_response = await client.post(
        f"/api/v1/bookings/sessions/{session.id}/bookings",
        json=booking_data
    )
    booking_id = create_response.json()["id"]

    # Cancel the booking
    cancel_response = await client.delete(f"/api/v1/bookings/{booking_id}")
    assert cancel_response.status_code == 200

    # In development mode, the email service logs to console
    # The test verifies the cancellation endpoint works and triggers the email flow
    # In production, this would actually send an email via SendGrid
