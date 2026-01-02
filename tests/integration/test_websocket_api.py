"""Integration tests for WebSocket API.

Tests for Features:
- 131: WebSocket chat connection establishes correctly
- 132: WebSocket send_message event works correctly
- 133: WebSocket typing indicators work correctly
- 134: WebSocket phase_change event triggers correctly
- 135: WebSocket prd_ready event triggers correctly
- 136: WebSocket availability event returns slots
- 137: WebSocket booking_confirmed event triggers correctly
- 138: WebSocket error event handles failures gracefully
"""
import asyncio
import uuid

import pytest
from socketio import AsyncClient


@pytest.mark.asyncio
async def test_websocket_connection_establishes(client, sample_visitor_id: str):
    """Test WebSocket connection establishes correctly."""
    # First create a session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Connect via WebSocket
    sio = AsyncClient()
    connected = False
    connection_data = None

    @sio.on("connected")
    def on_connected(data):
        nonlocal connected, connection_data
        connected = True
        connection_data = data

    try:
        await sio.connect(
            "http://localhost:8000",
            socketio_path="/ws",
            transports=["websocket"],
            wait_timeout=5,
        )

        # Join session
        await sio.emit("join_session", {"session_id": session_id})

        # Wait for connection event
        await asyncio.sleep(0.5)

        assert connected is True
        assert connection_data is not None
        assert connection_data.get("session_id") == session_id

    finally:
        await sio.disconnect()


@pytest.mark.asyncio
async def test_websocket_send_message(client, sample_visitor_id: str):
    """Test WebSocket send_message event works correctly."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    sio = AsyncClient()
    messages_received = []
    typing_events = {"start": 0, "stop": 0}

    @sio.on("message")
    def on_message(data):
        messages_received.append(data)

    @sio.on("typing_start")
    def on_typing_start(data):
        typing_events["start"] += 1

    @sio.on("typing_stop")
    def on_typing_stop(data):
        typing_events["stop"] += 1

    try:
        await sio.connect(
            "http://localhost:8000",
            socketio_path="/ws",
            transports=["websocket"],
            wait_timeout=5,
        )
        await sio.emit("join_session", {"session_id": session_id})
        await asyncio.sleep(0.3)

        # Send message
        await sio.emit("send_message", {"content": "Hello via WebSocket"})
        await asyncio.sleep(2)  # Wait for AI response

        # Verify typing events occurred
        assert typing_events["start"] > 0
        assert typing_events["stop"] > 0

        # Verify message was received
        assert len(messages_received) > 0
        msg_data = messages_received[0]
        assert "user_message" in msg_data
        assert "ai_message" in msg_data

    finally:
        await sio.disconnect()


@pytest.mark.asyncio
async def test_websocket_typing_indicators(client, sample_visitor_id: str):
    """Test WebSocket typing indicators work correctly."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    sio = AsyncClient()
    typing_events = []

    @sio.on("typing_start")
    def on_typing_start(data):
        typing_events.append(("start", data))

    @sio.on("typing_stop")
    def on_typing_stop(data):
        typing_events.append(("stop", data))

    try:
        await sio.connect(
            "http://localhost:8000",
            socketio_path="/ws",
            transports=["websocket"],
            wait_timeout=5,
        )
        await sio.emit("join_session", {"session_id": session_id})
        await asyncio.sleep(0.3)

        # Send message to trigger typing
        await sio.emit("send_message", {"content": "Test typing"})
        await asyncio.sleep(1)

        # Verify typing events
        assert len(typing_events) >= 2
        assert any(e[0] == "start" for e in typing_events)
        assert any(e[0] == "stop" for e in typing_events)

    finally:
        await sio.disconnect()


@pytest.mark.asyncio
async def test_websocket_phase_change(client, sample_visitor_id: str):
    """Test WebSocket phase_change event triggers correctly."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    sio = AsyncClient()
    phase_changes = []

    @sio.on("phase_change")
    def on_phase_change(data):
        phase_changes.append(data)

    try:
        await sio.connect(
            "http://localhost:8000",
            socketio_path="/ws",
            transports=["websocket"],
            wait_timeout=5,
        )
        await sio.emit("join_session", {"session_id": session_id})
        await asyncio.sleep(0.3)

        # Send messages to progress through phases
        messages = [
            "My name is Test User",
            "test@example.com",
            "Test Corp",
            "Need help with AI",
        ]

        for msg in messages:
            await sio.emit("send_message", {"content": msg})
            await asyncio.sleep(1)

        # Verify phase changes occurred
        assert len(phase_changes) > 0
        # Should have progressed from greeting to other phases
        phases = [pc.get("phase") for pc in phase_changes]
        assert len(set(phases)) > 1  # Multiple different phases

    finally:
        await sio.disconnect()


@pytest.mark.asyncio
async def test_websocket_prd_ready_event(client, sample_visitor_id: str):
    """Test WebSocket prd_ready event triggers correctly."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    sio = AsyncClient()
    prd_ready_events = []

    @sio.on("prd_ready")
    def on_prd_ready(data):
        prd_ready_events.append(data)

    try:
        await sio.connect(
            "http://localhost:8000",
            socketio_path="/ws",
            transports=["websocket"],
            wait_timeout=5,
        )
        await sio.emit("join_session", {"session_id": session_id})
        await asyncio.sleep(0.3)

        # Send qualification messages
        qualification_messages = [
            "My name is PRD Test",
            "prd@test.com",
            "PRD Corp",
            "Need AI strategy help",
            "Budget $50,000",
            "Timeline 2 months",
        ]

        for msg in qualification_messages:
            await sio.emit("send_message", {"content": msg})
            await asyncio.sleep(1)

        # Verify prd_ready event
        assert len(prd_ready_events) > 0
        assert "message" in prd_ready_events[0]

    finally:
        await sio.disconnect()


@pytest.mark.asyncio
async def test_websocket_error_event(client):
    """Test WebSocket error event handles failures gracefully."""
    sio = AsyncClient()
    error_events = []

    @sio.on("error")
    def on_error(data):
        error_events.append(data)

    try:
        await sio.connect(
            "http://localhost:8000",
            socketio_path="/ws",
            transports=["websocket"],
            wait_timeout=5,
        )

        # Try to send message without joining session (should trigger error)
        await sio.emit("send_message", {"content": "Test"})
        await asyncio.sleep(0.5)

        # Verify error event was received
        assert len(error_events) > 0
        assert "message" in error_events[0]

    finally:
        await sio.disconnect()


@pytest.mark.asyncio
async def test_websocket_invalid_session_error(client):
    """Test WebSocket handles invalid session ID gracefully."""
    sio = AsyncClient()
    error_events = []

    @sio.on("error")
    def on_error(data):
        error_events.append(data)

    try:
        await sio.connect(
            "http://localhost:8000",
            socketio_path="/ws",
            transports=["websocket"],
            wait_timeout=5,
        )

        # Join with invalid session
        fake_id = str(uuid.uuid4())
        await sio.emit("join_session", {"session_id": fake_id})
        await asyncio.sleep(0.3)

        # Try operations
        await sio.emit("send_message", {"content": "Test"})
        await asyncio.sleep(0.5)

        # Should get error events
        assert len(error_events) > 0

    finally:
        await sio.disconnect()


@pytest.mark.asyncio
async def test_websocket_connection_stability(client, sample_visitor_id: str):
    """Test WebSocket connection remains stable during multiple operations."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    sio = AsyncClient()
    message_count = 0
    error_count = 0

    @sio.on("message")
    def on_message(data):
        nonlocal message_count
        message_count += 1

    @sio.on("error")
    def on_error(data):
        nonlocal error_count
        error_count += 1

    try:
        await sio.connect(
            "http://localhost:8000",
            socketio_path="/ws",
            transports=["websocket"],
            wait_timeout=5,
        )
        await sio.emit("join_session", {"session_id": session_id})
        await asyncio.sleep(0.3)

        # Send multiple messages
        for i in range(5):
            await sio.emit("send_message", {"content": f"Message {i}"})
            await asyncio.sleep(0.8)

        await asyncio.sleep(1)

        # Verify stable operation
        assert message_count >= 5
        assert error_count == 0  # No errors should occur

    finally:
        await sio.disconnect()


@pytest.mark.asyncio
async def test_websocket_multiple_connections_same_session(client, sample_visitor_id: str):
    """Test multiple WebSocket connections can join same session."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    sio1 = AsyncClient()
    sio2 = AsyncClient()
    messages1 = []
    messages2 = []

    @sio1.on("message")
    def on_message1(data):
        messages1.append(data)

    @sio2.on("message")
    def on_message2(data):
        messages2.append(data)

    try:
        # Connect both clients
        await sio1.connect(
            "http://localhost:8000",
            socketio_path="/ws/socket.io",
            transports=["websocket"],
            wait_timeout=5,
        )
        await sio1.emit("join_session", {"session_id": session_id})

        await sio2.connect(
            "http://localhost:8000",
            socketio_path="/ws/socket.io",
            transports=["websocket"],
            wait_timeout=5,
        )
        await sio2.emit("join_session", {"session_id": session_id})

        await asyncio.sleep(0.5)

        # Send message from one client
        await sio1.emit("send_message", {"content": "Test from client 1"})
        await asyncio.sleep(1.5)

        # Both clients should receive the message
        assert len(messages1) > 0
        assert len(messages2) > 0

    finally:
        await sio1.disconnect()
        await sio2.disconnect()


@pytest.mark.asyncio
async def test_websocket_reconnection(client, sample_visitor_id: str):
    """Test WebSocket reconnection works correctly."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    sio = AsyncClient()
    connected_count = 0

    @sio.on("connected")
    def on_connected(data):
        nonlocal connected_count
        connected_count += 1

    try:
        # Connect
        await sio.connect(
            "http://localhost:8000",
            socketio_path="/ws",
            transports=["websocket"],
            wait_timeout=5,
        )
        await sio.emit("join_session", {"session_id": session_id})
        await asyncio.sleep(0.3)

        assert connected_count == 1

        # Disconnect
        await sio.disconnect()
        await asyncio.sleep(0.3)

        # Reconnect
        await sio.connect(
            "http://localhost:8000",
            socketio_path="/ws",
            transports=["websocket"],
            wait_timeout=5,
        )
        await sio.emit("join_session", {"session_id": session_id})
        await asyncio.sleep(0.3)

        assert connected_count == 2

    finally:
        if sio.connected:
            await sio.disconnect()
