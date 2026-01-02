"""Integration tests for long conversation support.

Tests for Feature:
- 125: Bot supports 20+ message conversations
"""

import pytest


@pytest.mark.asyncio
async def test_conversation_with_25_messages(client, sample_visitor_id: str):
    """Test that bot handles 25+ message conversations correctly."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Send 25 messages
    messages = []
    for i in range(25):
        if i == 0:
            msg = "My name is John Doe"
        elif i == 1:
            msg = "My email is john@example.com"
        elif i == 2:
            msg = "I work at TechCorp"
        elif i == 3:
            msg = "We need help with AI strategy"
        elif i == 4:
            msg = "Budget is around $75,000"
        elif i == 5:
            msg = "Timeline is 2-3 months"
        else:
            msg = f"Follow-up question {i}: Can you tell me more about option {i}?"

        messages.append(msg)
        response = await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": msg},
        )
        assert response.status_code == 201

    # Verify session has all messages
    get_response = await client.get(f"/api/v1/sessions/{session_id}")
    session_data = get_response.json()

    # Should have: 1 welcome + 25 user messages + 25 AI responses = 51 messages
    assert len(session_data["messages"]) >= 50

    # Verify message order is preserved
    timestamps = [msg["created_at"] for msg in session_data["messages"]]
    assert timestamps == sorted(timestamps)


@pytest.mark.asyncio
async def test_context_retention_across_30_messages(client, sample_visitor_id: str):
    """Test that bot retains context across 30+ messages."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Send initial info
    await client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"content": "My name is Alice Smith"},
    )
    await client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"content": "I work at InnovateCo"},
    )
    await client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"content": "We need data analytics help"},
    )

    # Send 27 follow-up messages
    for i in range(27):
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": f"More details about requirement {i}"},
        )

    # Get session and verify context is preserved
    get_response = await client.get(f"/api/v1/sessions/{session_id}")
    session_data = get_response.json()

    # Check client_info is populated
    assert session_data["client_info"]["name"] == "Alice Smith"
    assert session_data["client_info"]["company"] == "InnovateCo"

    # Check business_context is populated
    assert "data analytics" in session_data["business_context"]["challenges"].lower()

    # Verify all messages are stored
    assert len(session_data["messages"]) >= 30


@pytest.mark.asyncio
async def test_session_data_size_handling(client, sample_visitor_id: str):
    """Test that session handles large data volumes."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Send messages with longer content
    long_messages = []
    for i in range(20):
        # Each message has substantial content
        msg = f"""
        This is message {i} with detailed information about our business needs.
        We are looking for comprehensive solutions that address multiple aspects:
        1. Data analytics and reporting
        2. Machine learning capabilities
        3. Integration with existing systems
        4. Scalability for future growth
        5. Security and compliance requirements

        Our budget range is ${50000 + i * 1000} and timeline is {2 + i} months.
        """
        long_messages.append(msg.strip())
        response = await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": msg.strip()},
        )
        assert response.status_code == 201

    # Verify session can be retrieved
    get_response = await client.get(f"/api/v1/sessions/{session_id}")
    assert get_response.status_code == 200

    session_data = get_response.json()
    assert len(session_data["messages"]) >= 20

    # Verify data integrity - check that content is preserved
    user_messages = [m for m in session_data["messages"] if m["role"] == "user"]
    assert len(user_messages) >= 20

    # Check first and last message content
    assert "message 0" in user_messages[0]["content"]
    assert "message 19" in user_messages[-1]["content"]


@pytest.mark.asyncio
async def test_prd_generation_after_long_conversation(client, sample_visitor_id: str):
    """Test PRD generation works after 20+ message conversation."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Send 20 messages to qualify
    messages = [
        "My name is Bob Johnson",
        "bob@longcorp.com",
        "LongConversation Inc",
        "We need help with digital transformation",
        "Budget is $100,000",
        "Timeline is 6 months",
    ]

    # Add more messages to reach 20
    for i in range(14):
        messages.append(f"Additional detail {i}")

    for msg in messages:
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": msg},
        )

    # Generate PRD
    prd_response = await client.post(
        "/api/v1/prd/generate",
        json={"session_id": session_id},
    )

    assert prd_response.status_code == 201
    prd_data = prd_response.json()

    # Verify PRD contains information from the conversation
    assert prd_data["client_name"] == "Bob Johnson"
    assert prd_data["client_company"] == "LongConversation Inc"
    assert len(prd_data["content_markdown"]) > 0


@pytest.mark.asyncio
async def test_message_order_preservation(client, sample_visitor_id: str):
    """Test that message order is preserved in long conversations."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Send 25 messages with specific order
    for i in range(25):
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": f"Message number {i:02d}"},
        )

    # Get session
    get_response = await client.get(f"/api/v1/sessions/{session_id}")
    session_data = get_response.json()

    # Extract user messages
    user_messages = [m for m in session_data["messages"] if m["role"] == "user"]

    # Verify order
    for i, msg in enumerate(user_messages):
        assert f"Message number {i:02d}" in msg["content"]


@pytest.mark.asyncio
async def test_session_retrieval_performance(client, sample_visitor_id: str):
    """Test that session retrieval is reasonable even with many messages."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Add 30 messages
    for i in range(30):
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": f"Test message {i}"},
        )

    # Time the retrieval
    import time
    start = time.time()
    get_response = await client.get(f"/api/v1/sessions/{session_id}")
    elapsed = time.time() - start

    assert get_response.status_code == 200
    # Should complete in reasonable time (< 2 seconds)
    assert elapsed < 2.0


@pytest.mark.asyncio
async def test_conversation_summary_generation_after_long_conversation(client, sample_visitor_id: str):
    """Test conversation summary generation works after long conversation."""
    # Create session
    create_response = await client.post(
        "/api/v1/sessions",
        json={"visitor_id": sample_visitor_id},
    )
    session_id = create_response.json()["id"]

    # Send 20+ messages
    for i in range(22):
        if i == 0:
            msg = "My name is Summary Test"
        elif i == 1:
            msg = "summary@test.com"
        elif i == 2:
            msg = "SummaryCorp"
        elif i == 3:
            msg = "Need AI and analytics"
        elif i == 4:
            msg = "Budget $80,000"
        elif i == 5:
            msg = "Timeline 4 months"
        else:
            msg = f"Detail {i}"

        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": msg},
        )

    # Generate summary
    summary_response = await client.post(
        "/api/v1/prd/generate-summary",
        json={"session_id": session_id},
    )

    assert summary_response.status_code == 200
    summary_data = summary_response.json()

    assert "summary" in summary_data
    assert len(summary_data["summary"]) > 0
    # Summary should reference key info
    summary_text = summary_data["summary"].lower()
    assert "summary test" in summary_text or "summarycorp" in summary_text
