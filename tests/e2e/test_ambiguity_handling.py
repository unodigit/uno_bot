"""E2E tests for Bot handles ambiguous responses with clarification feature.

This test suite verifies that the bot correctly detects ambiguous user responses
and asks for clarification before continuing the conversation.
"""

import pytest
from playwright.sync_api import Page, expect


class TestAmbiguityHandlingAPI:
    """Test ambiguity handling via API (using test client)."""

    @pytest.mark.asyncio
    async def test_bot_detects_uncertainty_and_asks_for_clarification(self, client):
        """Test that bot detects uncertainty keywords and asks for clarification."""
        print("\n=== Test: Bot detects uncertainty and asks for clarification ===")

        # Create session
        response = await client.post(
            "/api/v1/sessions",
            json={
                "visitor_id": "test-visitor-ambiguity",
                "source_url": "http://localhost:5173/test",
                "user_agent": "E2E Test"
            }
        )
        assert response.status_code in [200, 201]
        session_data = response.json()
        session_id = session_data["id"]
        print(f"✓ Created session: {session_id}")

        # Send ambiguous message with uncertainty
        response = await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "maybe"}
        )
        assert response.status_code in [200, 201]
        print("✓ Sent message: 'maybe'")

        # Get updated session to check bot response
        response = await client.get(f"/api/v1/sessions/{session_id}")
        session = response.json()
        messages = session["messages"]

        # Find the bot's response
        bot_messages = [m for m in messages if m["role"] == "assistant"]
        last_bot_message = bot_messages[-1]

        print(f"✓ Bot response: {last_bot_message['content'][:100]}...")

        # Verify it's a clarification response
        assert last_bot_message["meta_data"]["type"] == "clarification"
        assert last_bot_message["meta_data"]["ambiguous_reason"] == "uncertainty"
        assert len(last_bot_message["content"]) > 0
        print("✅ Bot correctly identified ambiguity and asked for clarification")

    @pytest.mark.asyncio
    async def test_bot_detects_lack_of_knowledge_and_asks_for_clarification(self, client):
        """Test that bot detects lack of knowledge and asks for clarification."""
        print("\n=== Test: Bot detects lack of knowledge and asks for clarification ===")

        # Create session
        response = await client.post(
            "/api/v1/sessions",
            json={
                "visitor_id": "test-visitor-ambiguity-2",
                "source_url": "http://localhost:5173/test",
                "user_agent": "E2E Test"
            }
        )
        session_id = response.json()["id"]

        # Send ambiguous message
        response = await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "not sure"}
        )
        print("✓ Sent message: 'not sure'")

        # Get updated session
        response = await client.get(f"/api/v1/sessions/{session_id}")
        session = response.json()
        messages = session["messages"]
        bot_messages = [m for m in messages if m["role"] == "assistant"]
        last_bot_message = bot_messages[-1]

        print(f"✓ Bot response: {last_bot_message['content'][:100]}...")

        # Verify clarification
        assert last_bot_message["meta_data"]["type"] == "clarification"
        assert last_bot_message["meta_data"]["ambiguous_reason"] == "lack_of_knowledge"
        print("✅ Bot correctly identified lack of knowledge and asked for clarification")

    @pytest.mark.asyncio
    async def test_bot_detects_minimal_response_and_asks_for_clarification(self, client):
        """Test that bot detects minimal yes/no responses and asks for clarification."""
        print("\n=== Test: Bot detects minimal response and asks for clarification ===")

        # Create session
        response = await client.post(
            "/api/v1/sessions",
            json={
                "visitor_id": "test-visitor-ambiguity-3",
                "source_url": "http://localhost:5173/test",
                "user_agent": "E2E Test"
            }
        )
        session_id = response.json()["id"]

        # Send minimal response
        response = await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "yes"}
        )
        print("✓ Sent message: 'yes'")

        # Get updated session
        response = await client.get(f"/api/v1/sessions/{session_id}")
        session = response.json()
        messages = session["messages"]
        bot_messages = [m for m in messages if m["role"] == "assistant"]
        last_bot_message = bot_messages[-1]

        print(f"✓ Bot response: {last_bot_message['content'][:100]}...")

        # Verify clarification
        assert last_bot_message["meta_data"]["type"] == "clarification"
        assert last_bot_message["meta_data"]["ambiguous_reason"] == "minimal_response"
        print("✅ Bot correctly identified minimal response and asked for clarification")

    @pytest.mark.asyncio
    async def test_bot_continues_conversation_after_clarification(self, client):
        """Test that bot continues normal conversation after receiving clarification."""
        print("\n=== Test: Bot continues conversation after clarification ===")

        # Create session
        response = await client.post(
            "/api/v1/sessions",
            json={
                "visitor_id": "test-visitor-ambiguity-4",
                "source_url": "http://localhost:5173/test",
                "user_agent": "E2E Test"
            }
        )
        session_id = response.json()["id"]

        # Step 1: Send ambiguous message
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "maybe"}
        )
        response = await client.get(f"/api/v1/sessions/{session_id}")
        bot_messages = [m for m in response.json()["messages"] if m["role"] == "assistant"]
        assert bot_messages[-1]["meta_data"]["type"] == "clarification"
        print("✓ Bot asked for clarification")

        # Step 2: Send clear response
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "I need help with my website"}
        )
        response = await client.get(f"/api/v1/sessions/{session_id}")
        bot_messages = [m for m in response.json()["messages"] if m["role"] == "assistant"]
        last_bot_message = bot_messages[-1]

        # Should NOT be a clarification message anymore
        assert last_bot_message["meta_data"].get("type") != "clarification"
        print(f"✓ Bot continued conversation: {last_bot_message['content'][:80]}...")
        print("✅ Bot correctly continued conversation after clarification")

    @pytest.mark.asyncio
    async def test_bot_accepts_valid_name_after_asking_for_it(self, client):
        """Test that bot accepts valid names without treating them as ambiguous."""
        print("\n=== Test: Bot accepts valid names ===")

        # Create session
        response = await client.post(
            "/api/v1/sessions",
            json={
                "visitor_id": "test-visitor-ambiguity-5",
                "source_url": "http://localhost:5173/test",
                "user_agent": "E2E Test"
            }
        )
        session_id = response.json()["id"]

        # Get the welcome message (bot asks for name)
        response = await client.get(f"/api/v1/sessions/{session_id}")
        welcome_message = response.json()["messages"][0]
        assert "name" in welcome_message["content"].lower()
        print("✓ Bot asked for name")

        # Send a valid name
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "John Smith"}
        )
        response = await client.get(f"/api/v1/sessions/{session_id}")
        bot_messages = [m for m in response.json()["messages"] if m["role"] == "assistant"]
        last_bot_message = bot_messages[-1]

        # Should NOT be a clarification message
        assert last_bot_message["meta_data"].get("type") != "clarification"
        print(f"✓ Bot accepted name and continued: {last_bot_message['content'][:80]}...")
        print("✅ Bot correctly accepted valid name")

    @pytest.mark.asyncio
    async def test_bot_accepts_valid_email(self, client):
        """Test that bot accepts valid email addresses."""
        print("\n=== Test: Bot accepts valid email ===")

        # Create session
        response = await client.post(
            "/api/v1/sessions",
            json={
                "visitor_id": "test-visitor-ambiguity-6",
                "source_url": "http://localhost:5173/test",
                "user_agent": "E2E Test"
            }
        )
        session_id = response.json()["id"]

        # First send name to progress conversation
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "John"}
        )
        # Then send email
        await client.post(
            f"/api/v1/sessions/{session_id}/messages",
            json={"content": "john@example.com"}
        )

        response = await client.get(f"/api/v1/sessions/{session_id}")
        session = response.json()

        # Check if email was extracted (in client_info)
        assert "john@example.com" in str(session.get("client_info", {}))
        print("✓ Bot accepted and extracted email")
        print("✅ Bot correctly accepts valid email addresses")


class TestAmbiguityHandlingUI:
    """Test ambiguity handling through the UI."""

    def test_ambiguity_handling_in_chat_widget(self, page: Page):
        """Test ambiguity handling through the chat widget UI."""
        print("\n=== Test: Ambiguity handling in Chat Widget UI ===")

        # Navigate to the main page
        page.goto("http://localhost:5173")
        page.wait_for_load_state("networkidle")

        # Wait for chat widget to load
        chat_widget = page.locator('[data-testid="chat-widget"]')
        expect(chat_widget).to_be_visible()
        print("✓ Chat widget loaded")

        # Open chat widget if not already open
        open_button = page.locator('button:has-text("Chat")')
        if open_button.is_visible():
            open_button.click()

        # Wait for chat input
        chat_input = page.locator('input[placeholder*="Type your message"]')
        expect(chat_input).to_be_visible()
        print("✓ Chat input visible")

        # Send ambiguous message
        chat_input.fill("maybe")
        send_button = page.locator('button:has-text("Send")')
        send_button.click()
        print("✓ Sent ambiguous message: 'maybe'")

        # Wait for bot response
        page.wait_for_timeout(2000)

        # Check for clarification message in chat
        chat_messages = page.locator('[data-testid="chat-message"]')
        last_message = chat_messages.last

        # The last message should be from bot and contain clarification
        message_text = last_message.inner_text()
        print(f"✓ Bot response: {message_text[:100]}...")

        # Verify it's a clarification (should ask for more details)
        assert "could" in message_text.lower() or "tell me" in message_text.lower()
        print("✅ UI correctly shows clarification message")

        # Now send a clear response
        chat_input.fill("I need help with my website")
        send_button.click()
        print("✓ Sent clear message: 'I need help with my website'")

        # Wait for bot response
        page.wait_for_timeout(2000)

        # Check that conversation continues
        new_last_message = chat_messages.last
        new_message_text = new_last_message.inner_text()
        print(f"✓ Bot continued: {new_message_text[:100]}...")

        # Should not be the same as the clarification message
        assert new_message_text != message_text
        print("✅ Conversation continues after clarification")
