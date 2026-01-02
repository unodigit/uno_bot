"""Integration tests for expert matching functionality."""
import uuid

import pytest
from httpx import AsyncClient

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
