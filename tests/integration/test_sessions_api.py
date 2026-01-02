"""Integration tests for session API endpoints."""
import uuid

import pytest


@pytest.mark.asyncio
async def test_create_session_endpoint(client, sample_visitor_id: str):
    """Test POST /api/v1/sessions creates a new session."""
    response = await client.post(
        "/api/v1/sessions",
        json={
            "visitor_id": sample_visitor_id,
            "source_url": "https://example.com",
            "user_agent": "TestAgent/1.0",
        },
    )

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["visitor_id"] == sample_visitor_id
    assert data["status"] == "active"
    assert data["current_phase"] == "greeting"
    assert data["source_url"] == "https://example.com"
    assert data["user_agent"] == "TestAgent/1.0"
    assert len(data["messages"]) == 1
    assert data["messages"][0]["role"] == "assistant"


@pytest.mark.asyncio
async def test_create_session_minimal(client, sample_visitor_id: str):
    """Test POST /api/v1/sessions with minimal required data."""
    response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["visitor_id"] == sample_visitor_id
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_get_session_endpoint(client, sample_visitor_id: str):
    """Test GET /api/v1/sessions/{id} retrieves session details."""
    # First create a session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Then retrieve it
    response = await client.get(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == session_id
    assert data["visitor_id"] == sample_visitor_id
    assert "messages" in data
    assert len(data["messages"]) >= 1


@pytest.mark.asyncio
async def test_get_session_not_found(client):
    """Test GET /api/v1/sessions/{id} returns 404 for non-existent session."""
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/sessions/{fake_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_send_message_endpoint(client, sample_visitor_id: str):
    """Test POST /api/v1/sessions/{id}/messages sends a message."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Send message
    response = await client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"content": "I need help with AI solutions"},
    )

    assert response.status_code == 201
    data = response.json()

    assert data["role"] == "user"
    assert data["content"] == "I need help with AI solutions"
    assert data["session_id"] == session_id


@pytest.mark.asyncio
async def test_send_message_to_nonexistent_session(client):
    """Test POST /api/v1/sessions/{id}/messages returns 404 for non-existent session."""
    fake_id = str(uuid.uuid4())
    response = await client.post(
        f"/api/v1/sessions/{fake_id}/messages",
        json={"content": "Test message"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_send_message_to_completed_session(client, db_session, sample_visitor_id: str):
    """Test POST /api/v1/sessions/{id}/messages fails for completed session."""

    from src.services.session_service import SessionService
    from src.schemas.session import SessionCreate

    # Use the same db_session that the client uses
    service = SessionService(db_session)
    session = await service.create_session(SessionCreate(visitor_id=sample_visitor_id))
    await service.complete_session(session)

    # Try to send message
    response = await client.post(
        f"/api/v1/sessions/{session.id}/messages",
        json={"content": "Test"},
    )

    assert response.status_code == 400
    assert "completed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_resume_session_endpoint(client, db_session, sample_visitor_id: str):
    """Test POST /api/v1/sessions/{id}/resume resumes a session."""
    from src.schemas.session import SessionCreate
    from src.services.session_service import SessionService

    # Use the same db_session that the client uses
    service = SessionService(db_session)
    session = await service.create_session(SessionCreate(visitor_id=sample_visitor_id))
    session.status = "abandoned"
    db_session.add(session)
    await db_session.commit()

    # Resume the session
    response = await client.post(
        "/api/v1/sessions/resume",
        json={"session_id": str(session.id)},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_resume_nonexistent_session(client):
    """Test POST /api/v1/sessions/resume returns 404 for non-existent session."""
    fake_id = str(uuid.uuid4())
    response = await client.post(
        "/api/v1/sessions/resume",
        json={"session_id": fake_id},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_session_message_order(client, sample_visitor_id: str):
    """Test that messages are returned in chronological order."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Send multiple messages
    await client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"content": "First message"},
    )
    await client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"content": "Second message"},
    )

    # Get session and check order
    response = await client.get(f"/api/v1/sessions/{session_id}")
    data = response.json()

    messages = data["messages"]
    assert len(messages) == 5  # Welcome + 2 user messages + 2 AI responses

    # Check timestamps are in order
    timestamps = [msg["created_at"] for msg in messages]
    assert timestamps == sorted(timestamps)


@pytest.mark.asyncio
async def test_session_activity_updates(client, sample_visitor_id: str):
    """Test that session activity timestamp updates on message send."""
    import time

    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Get initial activity time
    get_response = await client.get(f"/api/v1/sessions/{session_id}")
    initial_activity = get_response.json()["last_activity"]

    # Small delay
    time.sleep(0.01)

    # Send message
    await client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"content": "Test"},
    )

    # Get updated session
    get_response = await client.get(f"/api/v1/sessions/{session_id}")
    updated_activity = get_response.json()["last_activity"]

    assert updated_activity > initial_activity
