"""Integration tests for experts list API.

Tests for Feature:
- 130: GET /api/v1/experts returns list of active experts
"""
import pytest

from src.schemas.expert import ExpertCreate
from src.services.expert_service import ExpertService


@pytest.mark.asyncio
async def test_list_experts_returns_active_only(client, db_session, sample_expert_data):
    """Test GET /api/v1/experts returns only active experts."""
    service = ExpertService(db_session)

    # Create multiple experts - some active, some inactive
    expert1_data = sample_expert_data.copy()
    expert1_data["email"] = f"active1.{expert1_data['email']}"
    expert1_response = await service.create_expert(ExpertCreate(**expert1_data))
    expert1 = await service.get_expert_model(expert1_response.id)

    expert2_data = sample_expert_data.copy()
    expert2_data["email"] = f"active2.{expert2_data['email']}"
    expert2_response = await service.create_expert(ExpertCreate(**expert2_data))
    expert2 = await service.get_expert_model(expert2_response.id)

    # Create an inactive expert
    inactive_data = sample_expert_data.copy()
    inactive_data["email"] = f"inactive.{inactive_data['email']}"
    inactive_data["name"] = "Inactive Expert"
    inactive_response = await service.create_expert(ExpertCreate(**inactive_data))
    inactive_expert = await service.get_expert_model(inactive_response.id)
    await service.deactivate_expert(inactive_expert)

    # Get experts list
    response = await client.get("/api/v1/experts")

    assert response.status_code == 200
    experts = response.json()

    # Should only return active experts
    assert len(experts) == 2

    # Verify all returned experts are active
    for expert in experts:
        assert expert["is_active"] is True
        assert "refresh_token" not in expert  # Sensitive data excluded

    # Verify correct experts are returned
    names = {expert["name"] for expert in experts}
    assert "Inactive Expert" not in names


@pytest.mark.asyncio
async def test_list_experts_returns_all_fields(client, db_session, sample_expert_data):
    """Test GET /api/v1/experts returns all required fields."""
    service = ExpertService(db_session)

    # Create an expert
    expert = await service.create_expert(ExpertCreate(**sample_expert_data))

    # Get experts list
    response = await client.get("/api/v1/experts")

    assert response.status_code == 200
    experts = response.json()

    # Should have at least our expert
    assert len(experts) >= 1

    # Find our expert
    our_expert = next((e for e in experts if e["email"] == sample_expert_data["email"]), None)
    assert our_expert is not None

    # Verify all required fields are present
    assert "id" in our_expert
    assert "name" in our_expert
    assert "email" in our_expert
    assert "photo_url" in our_expert
    assert "role" in our_expert
    assert "bio" in our_expert
    assert "specialties" in our_expert
    assert "services" in our_expert
    assert "is_active" in our_expert

    # Verify values match
    assert our_expert["name"] == sample_expert_data["name"]
    assert our_expert["email"] == sample_expert_data["email"]
    assert our_expert["role"] == sample_expert_data["role"]
    assert our_expert["bio"] == sample_expert_data["bio"]
    assert our_expert["specialties"] == sample_expert_data["specialties"]
    assert our_expert["services"] == sample_expert_data["services"]
    assert our_expert["is_active"] is True


@pytest.mark.asyncio
async def test_list_experts_empty_when_no_experts(client):
    """Test GET /api/v1/experts returns empty list when no experts exist."""
    response = await client.get("/api/v1/experts")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_experts_excludes_sensitive_data(client, db_session, sample_expert_data):
    """Test GET /api/v1/experts excludes sensitive information."""
    service = ExpertService(db_session)

    # Create an expert with refresh token
    expert_response = await service.create_expert(ExpertCreate(**sample_expert_data))
    expert = await service.get_expert_model(expert_response.id)
    expert.refresh_token = "secret_refresh_token_12345"
    db_session.add(expert)
    await db_session.commit()

    # Get experts list
    response = await client.get("/api/v1/experts")

    assert response.status_code == 200
    experts = response.json()

    # Find our expert
    our_expert = next((e for e in experts if e["email"] == sample_expert_data["email"]), None)
    assert our_expert is not None

    # Verify sensitive data is excluded
    assert "refresh_token" not in our_expert
    assert "password" not in our_expert
    assert "secret" not in our_expert


@pytest.mark.asyncio
async def test_list_experts_response_format(client, db_session, sample_expert_data):
    """Test GET /api/v1/experts returns correct response format."""
    service = ExpertService(db_session)
    await service.create_expert(ExpertCreate(**sample_expert_data))

    response = await client.get("/api/v1/experts")

    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("application/json")

    # Verify response is a list
    experts = response.json()
    assert isinstance(experts, list)

    # Verify each expert has correct structure
    for expert in experts:
        assert isinstance(expert, dict)
        assert isinstance(expert["id"], str)
        assert isinstance(expert["name"], str)
        assert isinstance(expert["email"], str)
        assert isinstance(expert["is_active"], bool)
        assert isinstance(expert["specialties"], list)
        assert isinstance(expert["services"], list)
