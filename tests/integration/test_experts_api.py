"""Integration tests for Expert CRUD operations."""
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.expert import Expert


@pytest.mark.asyncio
async def test_create_expert(db_session: AsyncSession, client: AsyncClient):
    """Test creating a new expert."""
    expert_data = {
        "name": "Dr. Sarah Johnson",
        "email": "sarah.johnson@example.com",
        "role": "AI Strategy Consultant",
        "bio": "Expert in AI/ML strategy with 10+ years experience",
        "photo_url": "https://example.com/photos/sarah.jpg",
        "specialties": ["AI Strategy", "Machine Learning", "Data Science"],
        "services": ["AI Strategy & Planning", "Data Intelligence & Analytics"],
        "calendar_id": "sarah.johnson@example.com",
        "availability": {
            "business_hours_start": "09:00",
            "business_hours_end": "17:00",
            "timezone": "America/New_York",
        },
    }

    response = await client.post("/api/v1/experts", json=expert_data)

    assert response.status_code == 201
    data = response.json()

    assert data["name"] == expert_data["name"]
    assert data["email"] == expert_data["email"]
    assert data["role"] == expert_data["role"]
    assert data["bio"] == expert_data["bio"]
    assert data["specialties"] == expert_data["specialties"]
    assert data["services"] == expert_data["services"]
    assert "id" in data
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_list_experts_empty(db_session: AsyncSession, client: AsyncClient):
    """Test listing experts when database is empty."""
    response = await client.get("/api/v1/experts")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_experts_with_data(
    db_session: AsyncSession, client: AsyncClient
):
    """Test listing experts with multiple experts in database."""
    # Create two experts
    expert1 = Expert(
        name="Dr. Sarah Johnson",
        email="sarah@example.com",
        role="AI Strategy Consultant",
        specialties=["AI Strategy"],
        services=["AI Strategy & Planning"],
        is_active=True,
    )
    expert2 = Expert(
        name="John Smith",
        email="john@example.com",
        role="Custom Dev Consultant",
        specialties=["Web Development"],
        services=["Custom Software Development"],
        is_active=True,
    )

    db_session.add(expert1)
    db_session.add(expert2)
    await db_session.commit()

    response = await client.get("/api/v1/experts")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Dr. Sarah Johnson"
    assert data[1]["name"] == "John Smith"


@pytest.mark.asyncio
async def test_get_expert_by_id(db_session: AsyncSession, client: AsyncClient):
    """Test getting a specific expert by ID."""
    expert = Expert(
        name="Dr. Sarah Johnson",
        email="sarah@example.com",
        role="AI Strategy Consultant",
        bio="AI expert with 10 years experience",
        specialties=["AI Strategy"],
        services=["AI Strategy & Planning"],
        is_active=True,
    )

    db_session.add(expert)
    await db_session.commit()
    await db_session.refresh(expert)

    response = await client.get(f"/api/v1/experts/{expert.id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(expert.id)
    assert data["name"] == "Dr. Sarah Johnson"
    assert data["email"] == "sarah@example.com"
    assert data["role"] == "AI Strategy Consultant"
    assert data["bio"] == "AI expert with 10 years experience"
    assert data["specialties"] == ["AI Strategy"]


@pytest.mark.asyncio
async def test_get_expert_not_found(db_session: AsyncSession, client: AsyncClient):
    """Test getting a non-existent expert returns 404."""
    fake_id = uuid.uuid4()

    response = await async_client.get(f"/api/v1/experts/{fake_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_expert(db_session: AsyncSession, client: AsyncClient):
    """Test updating an expert."""
    expert = Expert(
        name="Dr. Sarah Johnson",
        email="sarah@example.com",
        role="AI Strategy Consultant",
        specialties=["AI Strategy"],
        services=["AI Strategy & Planning"],
        is_active=True,
    )

    db_session.add(expert)
    await db_session.commit()
    await db_session.refresh(expert)

    update_data = {
        "name": "Dr. Sarah Johnson, PhD",
        "bio": "AI expert with 15 years experience and a PhD",
        "specialties": ["AI Strategy", "Deep Learning"],
    }

    response = await async_client.put(
        f"/api/v1/experts/{expert.id}", json=update_data
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(expert.id)
    assert data["name"] == "Dr. Sarah Johnson, PhD"
    assert data["bio"] == "AI expert with 15 years experience and a PhD"
    assert data["specialties"] == ["AI Strategy", "Deep Learning"]
    # Original email should remain unchanged
    assert data["email"] == "sarah@example.com"


@pytest.mark.asyncio
async def test_update_expert_not_found(
    db_session: AsyncSession, async_client: AsyncClient
):
    """Test updating a non-existent expert returns 404."""
    fake_id = uuid.uuid4()
    update_data = {"name": "New Name"}

    response = await async_client.put(f"/api/v1/experts/{fake_id}", json=update_data)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_expert(db_session: AsyncSession, async_client: AsyncClient):
    """Test deleting an expert."""
    expert = Expert(
        name="Dr. Sarah Johnson",
        email="sarah@example.com",
        role="AI Strategy Consultant",
        specialties=["AI Strategy"],
        services=["AI Strategy & Planning"],
        is_active=True,
    )

    db_session.add(expert)
    await db_session.commit()
    await db_session.refresh(expert)

    expert_id = expert.id

    response = await async_client.delete(f"/api/v1/experts/{expert_id}")

    assert response.status_code == 204

    # Verify expert is deleted
    get_response = await async_client.get(f"/api/v1/experts/{expert_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_expert_not_found(
    db_session: AsyncSession, async_client: AsyncClient
):
    """Test deleting a non-existent expert returns 404."""
    fake_id = uuid.uuid4()

    response = await async_client.delete(f"/api/v1/experts/{fake_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_inactive_expert_not_listed(
    db_session: AsyncSession, async_client: AsyncClient
):
    """Test that inactive experts are not returned in list."""
    # Create active and inactive experts
    active_expert = Expert(
        name="Active Expert",
        email="active@example.com",
        role="Consultant",
        specialties=["Consulting"],
        services=["Consulting"],
        is_active=True,
    )
    inactive_expert = Expert(
        name="Inactive Expert",
        email="inactive@example.com",
        role="Consultant",
        specialties=["Consulting"],
        services=["Consulting"],
        is_active=False,
    )

    db_session.add(active_expert)
    db_session.add(inactive_expert)
    await db_session.commit()

    response = await async_client.get("/api/v1/experts")

    assert response.status_code == 200
    data = response.json()

    # Should only return active expert
    assert len(data) == 1
    assert data[0]["name"] == "Active Expert"


@pytest.mark.asyncio
async def test_deactivate_expert(db_session: AsyncSession, async_client: AsyncClient):
    """Test deactivating an expert via update."""
    expert = Expert(
        name="Dr. Sarah Johnson",
        email="sarah@example.com",
        role="AI Strategy Consultant",
        specialties=["AI Strategy"],
        services=["AI Strategy & Planning"],
        is_active=True,
    )

    db_session.add(expert)
    await db_session.commit()
    await db_session.refresh(expert)

    # Deactivate the expert
    update_data = {"is_active": False}
    response = await async_client.put(
        f"/api/v1/experts/{expert.id}", json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False

    # Verify expert no longer appears in list
    list_response = await async_client.get("/api/v1/experts")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 0


@pytest.mark.asyncio
async def test_connect_calendar_oauth_flow(
    db_session: AsyncSession, client: AsyncClient
):
    """Test initiating Google Calendar OAuth flow."""
    expert = Expert(
        name="Dr. Sarah Johnson",
        email="sarah@example.com",
        role="AI Strategy Consultant",
        specialties=["AI Strategy"],
        services=["AI Strategy & Planning"],
        is_active=True,
    )

    db_session.add(expert)
    await db_session.commit()
    await db_session.refresh(expert)

    response = await client.post(
        f"/api/v1/experts/{expert.id}/connect_calendar"
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["message"] is not None
    assert "test-oauth" in data["message"]  # Should contain OAuth URL (test or Google)
    assert data["calendar_id"] is None


@pytest.mark.asyncio
async def test_connect_calendar_expert_not_found(
    db_session: AsyncSession, client: AsyncClient
):
    """Test connecting calendar for non-existent expert returns 404."""
    fake_id = uuid.uuid4()

    response = await client.post(
        f"/api/v1/experts/{fake_id}/connect_calendar"
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_oauth_callback_without_code(
    db_session: AsyncSession, client: AsyncClient
):
    """Test OAuth callback without authorization code returns 422."""
    response = await client.get("/api/v1/experts/calendar/callback")

    assert response.status_code == 422  # Pydantic validation error for missing required field


@pytest.mark.asyncio
async def test_oauth_callback_with_code_no_expert_id(
    db_session: AsyncSession, client: AsyncClient
):
    """Test OAuth callback with code but no expert ID returns 400."""
    response = await client.get(
        "/api/v1/experts/calendar/callback?code=fake_code"
    )

    assert response.status_code == 400
    assert "Expert ID is required" in response.json()["detail"]


@pytest.mark.asyncio
async def test_oauth_callback_expert_not_found(
    db_session: AsyncSession, client: AsyncClient
):
    """Test OAuth callback for non-existent expert returns 404."""
    fake_id = uuid.uuid4()

    response = await client.get(
        f"/api/v1/experts/calendar/callback?code=fake_code&expert_id={fake_id}"
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
