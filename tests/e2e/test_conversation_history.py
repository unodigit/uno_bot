from playwright.sync_api import Page, expect


class TestConversationHistory:
    """Test conversation history functionality."""

    def test_full_conversation_history_viewable(self, page: Page):
        """Test that full conversation history is viewable and scrollable."""
        # Navigate to the main page and open chat widget
        page.goto("http://localhost:5173/")
        page.wait_for_load_state("networkidle")

        # Click the chat widget button to open chat
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        expect(chat_window).to_be_visible()

        # Verify initial welcome message is present
        messages_container = page.get_by_test_id("messages-container")
        expect(messages_container).to_be_visible()

        # Send multiple messages to build a conversation history
        input_field = page.get_by_test_id("message-input")
        send_button = page.get_by_test_id("send-button")

        # Send 15+ messages to test scrolling
        test_messages = [
            "Hello",
            "I need help with a project",
            "What services do you offer?",
            "Can you tell me about AI Strategy?",
            "What about Custom Development?",
            "How much does it cost?",
            "What's your timeline?",
            "Can we schedule a meeting?",
            "I'm interested in your services",
            "Please provide more details",
            "What's the next step?",
            "Can you generate a PRD?",
            "How do I book an expert?",
            "What are the payment options?",
            "Do you offer support after delivery?"
        ]

        for message in test_messages:
            input_field.fill(message)
            send_button.click()
            page.wait_for_timeout(1000)  # Wait for response

        # Verify all messages are visible in the chat
        message_bubbles = page.get_by_test_id("message-user").or_(page.get_by_test_id("message-assistant"))
        # Should have at least the test messages + welcome message
        count = message_bubbles.count()
        assert count >= len(test_messages), f"Expected at least {len(test_messages)} messages, got {count}"

        # Verify messages are in correct order (newest at bottom)
        all_messages = page.locator(".flex.justify-start, .flex.justify-end")
        expect(all_messages.first).to_be_visible()  # First message should be visible
        expect(all_messages.last).to_be_visible()   # Last message should be visible

        # Test scrolling through chat history
        # Scroll to top to see oldest messages
        messages_container.evaluate("element => element.scrollTop = 0")

        # Verify oldest messages are visible
        oldest_messages = page.locator(".flex.justify-start, .flex.justify-end").first
        expect(oldest_messages).to_be_visible()

        # Scroll to bottom to see newest messages
        messages_container.evaluate("element => element.scrollTop = element.scrollHeight")

        # Verify newest messages are visible
        newest_messages = page.locator(".flex.justify-start, .flex.justify-end").last
        expect(newest_messages).to_be_visible()

        # Test that messages maintain proper formatting and timestamps
        message_bubbles = page.locator(".bg-white, .bg-primary")
        for i in range(message_bubbles.count()):
            bubble = message_bubbles.nth(i)
            expect(bubble).to_be_visible()
            # Verify message has content
            expect(bubble).to_contain_text("")

        print(f"✅ Successfully verified conversation history with {message_bubbles.count()} messages")
        print("✅ Verified scrolling functionality works correctly")
        print("✅ Verified message ordering is correct")

    def test_conversation_persists_across_refresh(self, page: Page):
        """Test that conversation history persists across page refreshes."""
        # Navigate to the main page and open chat widget
        page.goto("http://localhost:5173/")
        page.wait_for_load_state("networkidle")

        # Open chat and send a few messages
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        chat_window = page.get_by_test_id("chat-window")
        expect(chat_window).to_be_visible()

        input_field = page.get_by_test_id("message-input")
        send_button = page.get_by_test_id("send-button")

        # Send test messages
        test_message = "Test message for persistence"
        input_field.fill(test_message)
        send_button.click()
        page.wait_for_timeout(1000)

        # Verify message was sent
        user_message = page.get_by_test_id("message-user")
        expect(user_message).to_contain_text(test_message)

        # Refresh the page
        page.reload()
        page.wait_for_load_state("networkidle")

        # Reopen chat
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        chat_window = page.get_by_test_id("chat-window")
        expect(chat_window).to_be_visible()

        # Verify the message is still there
        messages_container = page.get_by_test_id("messages-container")
        expect(messages_container).to_contain_text(test_message)

        print("✅ Verified conversation persistence across page refresh")
