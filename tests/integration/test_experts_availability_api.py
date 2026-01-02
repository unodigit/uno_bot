"""Integration tests for experts availability API endpoint.

Tests for feature: GET /api/v1/experts/{id}/availability returns time slots
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_expert_availability_success(client: AsyncClient, db_session: AsyncSession):
    """Test GET /api/v1/experts/{id}/availability returns time slots."""
    # Create a test expert first
    from src.schemas.expert import ExpertCreate
    from src.services.expert_service import ExpertService

    expert_service = ExpertService(db_session)
    expert_create = ExpertCreate(
        name="Test Expert",
        email="test@example.com",
        role="Test Role",
        bio="Test bio",
        specialties=["AI", "ML"],
        services=["AI Strategy"]
    )
    expert = await expert_service.create_expert(expert_create)
    expert_id = str(expert.id)

    # Test availability with timezone
    response = await client.get(
        f"/api/v1/experts/{expert_id}/availability",
        params={
            "days_ahead": 14,
            "timezone": "America/New_York"
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "expert_id" in data
    assert "expert_name" in data
    assert "expert_role" in data
    assert "timezone" in data
    assert "slots" in data

    # Verify data types
    assert isinstance(data["slots"], list)
    assert data["expert_id"] == expert_id
    assert data["timezone"] == "America/New_York"

    # Verify we have at least 5 slots (as per feature requirement)
    assert len(data["slots"]) >= 5

    # Verify slot structure
    if len(data["slots"]) > 0:
        slot = data["slots"][0]
        assert "start_time" in slot
        assert "end_time" in slot
        assert "timezone" in slot
        assert "display_time" in slot
        assert "display_date" in slot


@pytest.mark.asyncio
async def test_get_expert_availability_different_timezone(client: AsyncClient, db_session: AsyncSession):
    """Test availability endpoint with different timezone."""
    from src.schemas.expert import ExpertCreate
    from src.services.expert_service import ExpertService

    expert_service = ExpertService(db_session)
    expert_create = ExpertCreate(
        name="Test Expert 2",
        email="test2@example.com",
        role="Test Role 2",
        bio="Test bio 2",
        specialties=["Data"],
        services=["Data Intelligence"]
    )
    expert = await expert_service.create_expert(expert_create)
    expert_id = str(expert.id)

    # Test with UTC timezone
    response = await client.get(
        f"/api/v1/experts/{expert_id}/availability",
        params={
            "days_ahead": 7,
            "timezone": "UTC"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["timezone"] == "UTC"
    assert len(data["slots"]) >= 5


@pytest.mark.asyncio
async def test_get_expert_availability_custom_params(client: AsyncClient, db_session: AsyncSession):
    """Test availability endpoint with custom parameters."""
    from src.schemas.expert import ExpertCreate
    from src.services.expert_service import ExpertService

    expert_service = ExpertService(db_session)
    expert_create = ExpertCreate(
        name="Test Expert 3",
        email="test3@example.com",
        role="Test Role 3",
        bio="Test bio 3",
        specialties=["Cloud"],
        services=["Custom Development"]
    )
    expert = await expert_service.create_expert(expert_create)
    expert_id = str(expert.id)

    # Test with custom days_ahead and min_slots_to_show
    response = await client.get(
        f"/api/v1/experts/{expert_id}/availability",
        params={
            "days_ahead": 7,
            "min_slots_to_show": 10,
            "timezone": "America/Los_Angeles"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["timezone"] == "America/Los_Angeles"


@pytest.mark.asyncio
async def test_get_expert_availability_invalid_expert(client: AsyncClient):
    """Test availability endpoint with invalid expert ID."""
    # Use a non-existent expert ID
    invalid_id = "00000000-0000-0000-0000-000000000000"

    response = await client.get(
        f"/api/v1/experts/{invalid_id}/availability",
        params={"days_ahead": 14}
    )

    # Should return 404 for non-existent expert
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_expert_availability_default_params(client: AsyncClient, db_session: AsyncSession):
    """Test availability endpoint with default parameters."""
    from src.schemas.expert import ExpertCreate
    from src.services.expert_service import ExpertService

    expert_service = ExpertService(db_session)
    expert_create = ExpertCreate(
        name="Test Expert 4",
        email="test4@example.com",
        role="Test Role 4",
        bio="Test bio 4",
        specialties=["Analytics"],
        services=["Analytics"]
    )
    expert = await expert_service.create_expert(expert_create)
    expert_id = str(expert.id)

    # Test without any parameters (use defaults)
    response = await client.get(
        f"/api/v1/experts/{expert_id}/availability"
    )

    assert response.status_code == 200
    data = response.json()
    assert "slots" in data
    assert isinstance(data["slots"], list)


@pytest.mark.asyncio
async def test_expert_list_endpoint(client: AsyncClient, db_session: AsyncSession):
    """Test GET /api/v1/experts returns list of active experts."""
    # Create a test expert
    from src.schemas.expert import ExpertCreate
    from src.services.expert_service import ExpertService

    expert_service = ExpertService(db_session)
    expert_create = ExpertCreate(
        name="Test Expert List",
        email="testlist@example.com",
        role="Test Role",
        bio="Test bio",
        specialties=["AI"],
        services=["AI Strategy"]
    )
    await expert_service.create_expert(expert_create)

    response = await client.get("/api/v1/experts")

    assert response.status_code == 200
    experts = response.json()

    # Verify response is a list
    assert isinstance(experts, list)

    # Verify we have at least one expert
    assert len(experts) > 0

    # Verify expert structure
    expert = experts[0]
    assert "id" in expert
    assert "name" in expert
    assert "email" in expert
    assert "role" in expert
    assert "is_active" in expert

    # Verify sensitive data is not included
    assert "refresh_token" not in expert
    assert "calendar_id" not in expert


@pytest.mark.asyncio
async def test_expert_detail_endpoint(client: AsyncClient, db_session: AsyncSession):
    """Test GET /api/v1/experts/{id} returns expert profile."""
    from src.schemas.expert import ExpertCreate
    from src.services.expert_service import ExpertService

    expert_service = ExpertService(db_session)
    expert_create = ExpertCreate(
        name="Test Expert Detail",
        email="testdetail@example.com",
        role="Test Role",
        bio="Test bio for detail",
        specialties=["AI", "ML"],
        services=["AI Strategy"]
    )
    expert = await expert_service.create_expert(expert_create)
    expert_id = str(expert.id)

    response = await client.get(f"/api/v1/experts/{expert_id}")

    assert response.status_code == 200
    expert = response.json()

    # Verify expert data
    assert expert["id"] == expert_id
    assert "name" in expert
    assert "email" in expert
    assert "role" in expert
    assert "bio" in expert
    assert "specialties" in expert
    assert "services" in expert
    assert "is_active" in expert

    # Verify sensitive data is not included
    assert "refresh_token" not in expert
    assert "calendar_id" not in expert


@pytest.mark.asyncio
async def test_expert_detail_not_found(client: AsyncClient):
    """Test GET /api/v1/experts/{id} with non-existent ID."""
    invalid_id = "00000000-0000-0000-0000-000000000000"

    response = await client.get(f"/api/v1/experts/{invalid_id}")

    assert response.status_code == 404
