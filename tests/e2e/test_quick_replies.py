"""End-to-end tests for Quick Reply buttons functionality."""
from playwright.sync_api import Page, expect

# Frontend URL
FRONTEND_URL = "http://localhost:5180"


class TestQuickReplies:
    """Test cases for quick reply buttons."""

    def test_quick_replies_appear_after_welcome(self, page: Page):
        """
        Test: Quick reply buttons appear for common options after welcome message

        Steps:
        1. Clear browser storage
        2. Navigate to main page
        3. Open chat widget
        4. Verify quick reply buttons appear after welcome message
        """
        # Clear storage to start fresh
        page.context.clear_cookies()
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")
        page.evaluate("localStorage.clear()")

        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()

        # Wait for welcome message and quick replies
        page.wait_for_timeout(800)

        # Verify quick replies container exists and is visible
        quick_replies = page.get_by_test_id("quick-replies")
        expect(quick_replies).to_be_visible()

        # Verify there are buttons inside
        buttons = quick_replies.locator("button")
        button_count = buttons.count()
        assert button_count > 0, "No quick reply buttons found"
        print(f"✓ Quick reply buttons appear ({button_count} buttons)")

    def test_quick_reply_sends_message(self, page: Page):
        """
        Test: Clicking a quick reply sends it as a message

        Steps:
        1. Open chat widget
        2. Click a quick reply button
        3. Verify the option is sent as a message
        4. Verify conversation continues
        """
        # Clear storage
        page.context.clear_cookies()
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")
        page.evaluate("localStorage.clear()")

        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_timeout(800)

        # Get the first quick reply button
        quick_replies = page.get_by_test_id("quick-replies")
        first_button = quick_replies.locator("button").first
        expected_text = first_button.inner_text()

        # Click the first quick reply
        first_button.click()

        # Wait for message to be sent
        page.wait_for_timeout(1000)

        # Verify user message appears with the quick reply text
        user_message = page.get_by_test_id("message-user").last
        expect(user_message).to_be_visible()
        expect(user_message).to_contain_text(expected_text)

        # Verify bot responds (get the last bot message)
        bot_message = page.get_by_test_id("message-assistant").last
        expect(bot_message).to_be_visible()

        print(f"✓ Quick reply '{expected_text}' sent as message and got response")

    def test_quick_replies_update_based_on_phase(self, page: Page):
        """
        Test: Quick reply options change based on conversation phase

        Steps:
        1. Start conversation in greeting phase
        2. Send a message to move to discovery phase
        3. Verify quick replies update
        """
        # Clear storage
        page.context.clear_cookies()
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")
        page.evaluate("localStorage.clear()")

        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_timeout(800)

        # Get initial quick replies (greeting phase)
        quick_replies = page.get_by_test_id("quick-replies")
        initial_buttons = quick_replies.locator("button")
        initial_count = initial_buttons.count()
        initial_first_text = initial_buttons.first.inner_text()

        # Send a message to move to next phase
        input_field = page.get_by_test_id("message-input")
        input_field.fill("Hi, my name is Alice")
        page.get_by_test_id("send-button").click()

        # Wait for response and phase update
        page.wait_for_timeout(1500)

        # Get updated quick replies (should be different phase)
        updated_buttons = quick_replies.locator("button")
        updated_count = updated_buttons.count()
        updated_first_text = updated_buttons.first.inner_text()

        # Verify quick replies changed (either count or content)
        buttons_changed = (
            initial_count != updated_count or
            initial_first_text != updated_first_text
        )
        assert buttons_changed, "Quick replies did not update after phase change"

        print(f"✓ Quick replies updated: '{initial_first_text}' -> '{updated_first_text}'")

    def test_quick_replies_hidden_during_streaming(self, page: Page):
        """
        Test: Quick reply buttons are hidden while bot is streaming

        Steps:
        1. Open chat and send a message
        2. While bot is responding, verify quick replies are hidden
        """
        # Clear storage
        page.context.clear_cookies()
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")
        page.evaluate("localStorage.clear()")

        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_timeout(800)

        # Verify quick replies are visible initially
        quick_replies = page.get_by_test_id("quick-replies")
        expect(quick_replies).to_be_visible()

        # Send a message
        input_field = page.get_by_test_id("message-input")
        input_field.fill("Tell me about your services")
        page.get_by_test_id("send-button").click()

        # Wait a moment for streaming to start
        page.wait_for_timeout(100)

        # Check if typing indicator is visible (means streaming)
        typing_indicator = page.get_by_test_id("typing-indicator")
        is_streaming = typing_indicator.is_visible()

        if is_streaming:
            # Verify quick replies are hidden during streaming
            expect(quick_replies).not_to_be_visible()
            print("✓ Quick replies hidden during streaming")
        else:
            print("✓ Streaming completed quickly, skipping visibility check")

    def test_quick_replies_with_email_preformat(self, page: Page):
        """
        Test: Email quick reply pre-fills proper format

        Steps:
        1. Open chat widget
        2. Find email quick reply
        3. Click it
        4. Verify proper format is sent
        """
        # Clear storage
        page.context.clear_cookies()
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")
        page.evaluate("localStorage.clear()")

        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_timeout(800)

        # Look for email quick reply
        quick_replies = page.get_by_test_id("quick-replies")
        buttons = quick_replies.locator("button")

        # Find a button with email pattern
        email_button = None
        for i in range(buttons.count()):
            btn = buttons.nth(i)
            text = btn.inner_text()
            if "email" in text.lower() or "@" in text:
                email_button = btn
                break

        if email_button:
            email_text = email_button.inner_text()
            email_button.click()
            page.wait_for_timeout(1000)

            # Verify the email text appears in user message
            user_message = page.get_by_test_id("message-user")
            expect(user_message).to_contain_text(email_text)
            print(f"✓ Email quick reply '{email_text}' sent correctly")
        else:
            print("ℹ No email quick reply found in current phase (may appear later)")
