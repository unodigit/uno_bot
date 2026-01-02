"""Integration tests for expert matching functionality."""
import uuid
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.models.booking import Booking
from src.schemas.expert import ExpertCreate


@pytest.mark.asyncio
async def test_match_experts_returns_ranked_list(
    client: AsyncClient, db_session, sample_visitor_id
):
    """Test that expert matching returns ranked experts with scores."""
    # Create test experts
    from src.services.expert_service import ExpertService

    service = ExpertService(db_session)

    # Expert 1: AI specialist
    await service.create_expert(
        ExpertCreate(
            name="AI Expert",
            email=f"ai.{uuid.uuid4().hex[:6]}@example.com",
            role="AI Consultant",
            bio="Expert in AI and ML",
            specialties=["AI", "Machine Learning"],
            services=["AI Strategy & Planning"],
        )
    )

    # Create a session
    response = await client.post(
        "/api/v1/sessions",
        json={
            "visitor_id": sample_visitor_id,
            "source_url": "http://test.com",
        },
    )
    assert response.status_code == 201
    session = response.json()
    session_id = session["id"]

    # Update session with service recommendation
    await client.patch(
        f"/api/v1/sessions/{session_id}",
        json={
            "recommended_service": "AI Strategy & Planning",
            "business_context": {"challenges": "Need AI implementation"},
        },
    )

    # Match experts
    response = await client.post(f"/api/v1/sessions/{session_id}/match-expert")
    assert response.status_code == 200
    match_result = response.json()

    # Should return experts with scores
    assert "experts" in match_result
    assert "match_scores" in match_result
    assert len(match_result["experts"]) == len(match_result["match_scores"])

    # Session should be updated with top expert
    response = await client.get(f"/api/v1/sessions/{session_id}")
    session_data = response.json()
    assert session_data["matched_expert_id"] is not None


@pytest.mark.asyncio
async def test_match_experts_empty_when_no_experts(
    client: AsyncClient, sample_visitor_id
):
    """Test expert matching returns empty list when no experts exist."""
    # Create a session
    response = await client.post(
        "/api/v1/sessions",
        json={
            "visitor_id": sample_visitor_id,
            "source_url": "http://test.com",
        },
    )
    assert response.status_code == 201
    session = response.json()
    session_id = session["id"]

    # Try to match experts (none exist)
    response = await client.post(f"/api/v1/sessions/{session_id}/match-expert")
    assert response.status_code == 200
    match_result = response.json()

    assert match_result["experts"] == []
    assert match_result["match_scores"] == []


@pytest.mark.asyncio
async def test_match_experts_404_for_nonexistent_session(
    client: AsyncClient,
):
    """Test expert matching returns 404 for non-existent session."""
    fake_id = uuid.uuid4()
    response = await client.post(f"/api/v1/sessions/{fake_id}/match-expert")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_match_experts_inactive_not_included(
    client: AsyncClient, db_session, sample_visitor_id
):
    """Test that inactive experts are excluded from matching."""
    from src.services.expert_service import ExpertService

    service = ExpertService(db_session)

    # Create inactive expert
    await service.create_expert(
        ExpertCreate(
            name="Inactive Expert",
            email=f"inactive.{uuid.uuid4().hex[:6]}@example.com",
            role="Consultant",
            bio="Not active",
            specialties=["AI"],
            services=["AI Strategy & Planning"],
            is_active=False,
        )
    )

    # Create active expert
    await service.create_expert(
        ExpertCreate(
            name="Active Expert",
            email=f"active.{uuid.uuid4().hex[:6]}@example.com",
            role="Consultant",
            bio="Active",
            specialties=["AI"],
            services=["AI Strategy & Planning"],
            is_active=True,
        )
    )

    # Create session
    response = await client.post(
        "/api/v1/sessions",
        json={
            "visitor_id": sample_visitor_id,
            "source_url": "http://test.com",
        },
    )
    assert response.status_code == 201
    session = response.json()
    session_id = session["id"]

    # Update session
    await client.patch(
        f"/api/v1/sessions/{session_id}",
        json={
            "recommended_service": "AI Strategy & Planning",
            "business_context": {"challenges": "AI needed"},
        },
    )

    # Match experts
    response = await client.post(f"/api/v1/sessions/{session_id}/match-expert")
    assert response.status_code == 200
    match_result = response.json()

    # Should only include active expert
    assert len(match_result["experts"]) == 1
    assert "active" in match_result["experts"][0]["email"]


@pytest.mark.asyncio
async def test_expert_workload_balancing_distributes_leads_evenly(
    client: AsyncClient, db_session, sample_visitor_id
):
    """Test that expert workload balancing distributes leads evenly.

    Feature: Expert workload balancing distributes leads evenly
    """
    from src.services.expert_service import ExpertService

    service = ExpertService(db_session)

    # Create two experts with identical qualifications
    expert1 = await service.create_expert(
        ExpertCreate(
            name="Expert One",
            email=f"expert1.{uuid.uuid4().hex[:6]}@example.com",
            role="AI Consultant",
            bio="Expert in AI",
            specialties=["AI", "Machine Learning"],
            services=["AI Strategy & Planning"],
            is_active=True,
        )
    )

    expert2 = await service.create_expert(
        ExpertCreate(
            name="Expert Two",
            email=f"expert2.{uuid.uuid4().hex[:6]}@example.com",
            role="AI Consultant",
            bio="Expert in AI",
            specialties=["AI", "Machine Learning"],
            services=["AI Strategy & Planning"],
            is_active=True,
        )
    )

    # Give expert1 5 existing bookings (high workload)
    now = datetime.utcnow()
    for i in range(5):
        booking = Booking(
            session_id=uuid.uuid4(),
            expert_id=expert1.id,
            title=f"Existing booking {i+1}",
            start_time=now + timedelta(days=i+1, hours=10),
            end_time=now + timedelta(days=i+1, hours=11),
            expert_email=expert1.email,
            client_email=f"client{i}@test.com",
            client_name=f"Client {i}",
            status="confirmed",
        )
        db_session.add(booking)
    await db_session.commit()

    # Create a session and match experts
    response = await client.post(
        "/api/v1/sessions",
        json={
            "visitor_id": sample_visitor_id,
            "source_url": "http://test.com",
        },
    )
    assert response.status_code == 201
    session = response.json()
    session_id = session["id"]

    await client.patch(
        f"/api/v1/sessions/{session_id}",
        json={
            "recommended_service": "AI Strategy & Planning",
            "business_context": {"challenges": "Need AI implementation"},
        },
    )

    # Match experts with workload balancing enabled
    response = await client.post(f"/api/v1/sessions/{session_id}/match-expert")
    assert response.status_code == 200
    match_result = response.json()

    # Verify both experts are returned
    assert len(match_result["experts"]) == 2
    assert len(match_result["match_scores"]) == 2

    # Find which expert is ranked first
    expert_ids = [exp["id"] for exp in match_result["experts"]]
    scores = match_result["match_scores"]

    # Expert 2 (no workload) should have higher score than Expert 1 (5 bookings)
    # Find positions
    expert1_index = expert_ids.index(str(expert1.id))
    expert2_index = expert_ids.index(str(expert2.id))

    # Expert 2 should be ranked higher (lower index) due to workload balancing
    assert scores[expert2_index] > scores[expert1_index], \
        f"Expert 2 (no workload) should have higher score than Expert 1 (5 bookings). " \
        f"Expert 1 score: {scores[expert1_index]}, Expert 2 score: {scores[expert2_index]}"


@pytest.mark.asyncio
async def test_workload_penalty_increases_with_more_bookings(
    db_session
):
    """Test that workload penalty decreases as expert bookings increase."""
    from src.schemas.expert import ExpertCreate
    from src.services.expert_service import ExpertService

    service = ExpertService(db_session)

    # Create expert
    expert = await service.create_expert(
        ExpertCreate(
            name="Test Expert",
            email=f"workload.{uuid.uuid4().hex[:6]}@example.com",
            role="AI Consultant",
            bio="Expert in AI",
            specialties=["AI"],
            services=["AI Strategy & Planning"],
            is_active=True,
        )
    )

    # Test workload penalty with different booking counts
    test_cases = [
        (0, 1.0),    # 0 bookings: 1.0 (no penalty)
        (1, 0.95),   # 1-2 bookings: 0.95
        (2, 0.95),   # 1-2 bookings: 0.95
        (3, 0.9),    # 3-4 bookings: 0.9
        (4, 0.9),    # 3-4 bookings: 0.9
        (5, 0.8),    # 5-6 bookings: 0.8
        (6, 0.8),    # 5-6 bookings: 0.8
        (7, 0.7),    # 7+ bookings: 0.7
        (10, 0.7),   # 7+ bookings: 0.7
    ]

    for booking_count, expected_penalty in test_cases:
        # Create bookings
        now = datetime.utcnow()
        for i in range(booking_count):
            booking = Booking(
                session_id=uuid.uuid4(),
                expert_id=expert.id,
                title=f"Booking {i+1}",
                start_time=now + timedelta(days=i+1, hours=10),
                end_time=now + timedelta(days=i+1, hours=11),
                expert_email=expert.email,
                client_email=f"client{i}@test.com",
                client_name=f"Client {i}",
                status="confirmed",
            )
            db_session.add(booking)
        await db_session.commit()

        # Get workload map
        workload_map = await service._get_expert_workload_counts()

        # Calculate penalty
        penalty = service._calculate_workload_penalty(expert.id, workload_map)

        assert penalty == expected_penalty, \
            f"Expected penalty {expected_penalty} for {booking_count} bookings, got {penalty}"

        # Clean up bookings for next iteration
        await db_session.execute(
            select(Booking).where(Booking.expert_id == expert.id)
        )
        # Delete all bookings
        from sqlalchemy import delete
        await db_session.execute(delete(Booking).where(Booking.expert_id == expert.id))
        await db_session.commit()
