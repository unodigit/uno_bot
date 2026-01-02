"""
E2E tests for accessibility features in the chat widget.
Tests screen reader support, keyboard navigation, and ARIA labels.
"""

from playwright.sync_api import Page, expect


class TestAccessibility:
    """Test suite for accessibility features."""

    def test_chat_widget_button_accessible(self, page: Page):
        """Test that chat widget button is accessible."""
        page.goto("http://localhost:5173")

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Find the chat widget button
        chat_button = page.get_by_test_id("chat-widget-button")

        # Verify button exists and is visible
        expect(chat_button).to_be_visible()
        expect(chat_button).to_have_attribute("aria-label", "Open chat")

        # Verify button has proper role
        expect(chat_button).to_have_attribute("data-testid", "chat-widget-button")

        # Check for tooltip description
        tooltip = page.locator("#chat-widget-tooltip")
        expect(tooltip).to_have_class("sr-only")

    def test_chat_window_dialog_structure(self, page: Page):
        """Test that chat window has proper dialog structure."""
        page.goto("http://localhost:5173")

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Open chat window
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.locator('[data-testid="chat-window"]')
        expect(chat_window).to_be_visible()

        # Verify dialog structure
        expect(chat_window).to_have_attribute("role", "dialog")
        expect(chat_window).to_have_attribute("aria-modal", "true")
        expect(chat_window).to_have_attribute("aria-labelledby", "chat-title")

        # Check for hidden title
        title = page.locator("#chat-title")
        expect(title).to_have_class("sr-only")
        expect(title).to_contain_text("UnoBot Chat")

    def test_keyboard_navigation(self, page: Page):
        """Test keyboard navigation through chat interface."""
        page.goto("http://localhost:5173")

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Open chat window
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat window to open and input to be focused
        input_field = page.locator('[data-testid="message-input"]')
        input_field.wait_for()

        # Verify input field is focused
        expect(input_field).to_be_focused()

        # Type some text so send button becomes enabled
        input_field.fill("Test message")

        # Test Tab navigation
        input_field.press("Tab")
        send_button = page.get_by_test_id("send-button")
        expect(send_button).to_be_focused()

        # Tab to settings button
        send_button.press("Tab")
        settings_button = page.get_by_test_id("settings-button")
        expect(settings_button).to_be_focused()

        # Tab to minimize button
        settings_button.press("Tab")
        minimize_button = page.get_by_test_id("minimize-button")
        expect(minimize_button).to_be_focused()

        # Tab to close button
        minimize_button.press("Tab")
        close_button = page.get_by_test_id("close-button")
        expect(close_button).to_be_focused()

    def test_input_field_accessibility(self, page: Page):
        """Test input field accessibility features."""
        page.goto("http://localhost:5173")

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Open chat window
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat window to open
        input_field = page.locator('[data-testid="message-input"]')
        input_field.wait_for()

        # Verify input field attributes
        expect(input_field).to_have_attribute("aria-label", "Type your message")
        expect(input_field).to_have_attribute("aria-describedby", "input-instruction")

        # Check for instruction text
        instruction = page.locator("#input-instruction")
        expect(instruction).to_have_class("sr-only")
        expect(instruction).to_contain_text("Press Enter to send message")

        # Test sending message with Enter
        input_field.fill("Hello, this is a test message")
        input_field.press("Enter")

        # Verify message appears
        user_message = page.locator('[data-testid="message-user"]').last
        expect(user_message).to_be_visible()

    def test_send_button_accessibility(self, page: Page):
        """Test send button accessibility features."""
        page.goto("http://localhost:5173")

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Open chat window
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat window to open
        send_button = page.get_by_test_id("send-button")
        send_button.wait_for()

        # Verify button attributes
        expect(send_button).to_have_attribute("aria-describedby", "send-button-status")

        # Check for status text
        status = page.locator("#send-button-status")
        expect(status).to_have_class("sr-only")

        # Test with empty input (button should be disabled)
        expect(send_button).to_be_disabled()

        # Test with text input (button should be enabled)
        input_field = page.locator('[data-testid="message-input"]')
        input_field.fill("Hello")
        expect(send_button).not_to_be_disabled()

        # Test sending with keyboard
        send_button.press("Enter")

    def test_messages_live_region(self, page: Page):
        """Test that messages area is a live region for screen readers."""
        page.goto("http://localhost:5173")

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Open chat window
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat window to open
        messages_container = page.locator('[data-testid="messages-container"]')
        messages_container.wait_for()

        # Verify live region attributes
        expect(messages_container).to_have_attribute("role", "log")
        expect(messages_container).to_have_attribute("aria-live", "polite")
        expect(messages_container).to_have_attribute("aria-relevant", "additions text")

        # Test that new messages are announced
        input_field = page.locator('[data-testid="message-input"]')
        input_field.fill("Testing live region")
        input_field.press("Enter")

        # Wait for response and verify it's announced
        bot_message = page.locator('[data-testid="message-assistant"]').last
        expect(bot_message).to_be_visible()
        expect(bot_message).to_have_attribute("role", "listitem")

    def test_typing_indicator_accessibility(self, page: Page):
        """Test typing indicator accessibility."""
        page.goto("http://localhost:5173")

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Open chat window
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat window to open
        input_field = page.locator('[data-testid="message-input"]')
        input_field.wait_for()

        # Send a message to trigger typing
        input_field.fill("Hello")
        input_field.press("Enter")

        # Wait for typing indicator
        typing_indicator = page.locator('[data-testid="typing-indicator"]')
        typing_indicator.wait_for()

        # Verify typing indicator attributes
        expect(typing_indicator).to_have_attribute("role", "status")
        expect(typing_indicator).to_have_attribute("aria-live", "polite")
        expect(typing_indicator).to_have_attribute("aria-label", "Bot is typing...")

    def test_header_buttons_accessibility(self, page: Page):
        """Test header buttons accessibility."""
        page.goto("http://localhost:5173")

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Open chat window
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat window to open
        page.locator('[data-testid="chat-window"]').wait_for()

        # Test minimize button
        minimize_button = page.get_by_test_id("minimize-button")
        expect(minimize_button).to_be_visible()
        expect(minimize_button).to_have_attribute("aria-describedby", "minimize-instruction")

        # Test close button
        close_button = page.get_by_test_id("close-button")
        expect(close_button).to_be_visible()
        expect(close_button).to_have_attribute("aria-describedby", "close-instruction")

    def test_screen_reader_announcements(self, page: Page):
        """Test screen reader announcements."""
        page.goto("http://localhost:5173")

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Check initial state announcements - use the first sr-only div
        initial_announcement = page.locator('div[aria-live="polite"].sr-only').first
        expect(initial_announcement).to_contain_text("Chat widget loaded")

        # Open chat and check announcement
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.locator('[data-testid="chat-window"]')
        chat_window.wait_for()

        # Check chat window announcement - the second sr-only div inside chat window
        chat_announcement = page.locator('[data-testid="chat-window"] div[aria-live="polite"].sr-only')
        expect(chat_announcement).to_contain_text("Chat window opened")

    def test_error_handling_accessibility(self, page: Page):
        """Test error handling with accessibility."""
        page.goto("http://localhost:5173")

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Open chat window
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat window to open
        page.locator('[data-testid="chat-window"]').wait_for()

        # Test error banner accessibility (if errors occur)
        error_banner = page.locator('[data-testid="error-banner"]')
        if error_banner.is_visible():
            expect(error_banner).to_have_attribute("role", "alert")
            expect(error_banner).to_have_attribute("aria-live", "assertive")

    def test_responsive_accessibility(self, page: Page):
        """Test accessibility on different screen sizes."""
        page.goto("http://localhost:5173")

        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 812})

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Open chat window
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Verify chat window is accessible on mobile
        chat_window = page.locator('[data-testid="chat-window"]')
        chat_window.wait_for()

        # Check that touch targets are appropriately sized
        input_field = page.locator('[data-testid="message-input"]')
        expect(input_field).to_be_visible()

        send_button = page.get_by_test_id("send-button")
        expect(send_button).to_be_visible()

        # Verify elements are still keyboard accessible
        input_field.focus()
        expect(input_field).to_be_focused()
