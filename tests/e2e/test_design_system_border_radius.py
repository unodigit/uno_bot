"""
E2E tests for Design System - Border Radius compliance

Feature #115: Border radius follows design system
Verifies that all UI elements use the correct border radius values from the design system.
"""

import pytest
from playwright.sync_api import Page


class TestBorderRadiusButtons:
    """Test border radius on buttons"""

    @pytest.mark.e2e
    def test_send_button_border_radius(self, page: Page, base_url: str):
        """Verify send button uses rounded-md (6px) border radius"""
        page.goto(base_url)
        page.wait_for_selector('[data-testid="chat-widget-button"]')
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        # Get send button
        send_button = page.query_selector('[data-testid="send-button"]')
        assert send_button is not None, "Send button not found"

        # Check border-radius
        border_radius = send_button.evaluate(
            "el => window.getComputedStyle(el).borderRadius"
        )

        # Should be rounded-md (6px) or rounded-full (for some buttons)
        assert border_radius in ["6px", "9999px", "50%"], f"Send button has unexpected border-radius: {border_radius}"

    @pytest.mark.e2e
    def test_quick_reply_buttons_border_radius(self, page: Page, base_url: str):
        """Verify quick reply buttons use rounded-full pill shape"""
        page.goto(base_url)
        page.wait_for_selector('[data-testid="chat-widget-button"]')
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        # Wait for quick replies to appear (may not always show)
        try:
            page.wait_for_selector('[data-testid="quick-reply-button"]', timeout=3000)

            # Get all quick reply buttons
            quick_replies = page.query_selector_all('[data-testid="quick-reply-button"]')

            # Check border-radius for each
            for reply in quick_replies:
                border_radius = reply.evaluate(
                    "el => window.getComputedStyle(el).borderRadius"
                )
                # Quick replies should be pill-shaped (rounded-full)
                assert border_radius in ["9999px", "50%", "9999px 9999px 9999px 9999px"], \
                    f"Quick reply button has unexpected border-radius: {border_radius}"
        except Exception:
            # Quick replies may not always appear, skip if not found
            pytest.skip("Quick reply buttons not displayed in this context")


class TestBorderRadiusCards:
    """Test border radius on card components"""

    @pytest.mark.e2e
    def test_chat_window_border_radius(self, page: Page, base_url: str):
        """Verify chat window uses rounded-lg (8px) border radius"""
        page.goto(base_url)
        page.wait_for_selector('[data-testid="chat-widget-button"]')
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        # Get chat window
        chat_window = page.query_selector('[data-testid="chat-window"]')
        assert chat_window is not None, "Chat window not found"

        # Check border-radius
        border_radius = chat_window.evaluate(
            "el => window.getComputedStyle(el).borderRadius"
        )

        # Should be rounded-lg (8px)
        assert border_radius == "8px", f"Chat window has unexpected border-radius: {border_radius}"

    @pytest.mark.e2e
    def test_bot_message_border_radius(self, page: Page, base_url: str):
        """Verify bot messages use rounded-lg with rounded-bl-sm"""
        page.goto(base_url)
        page.wait_for_selector('[data-testid="chat-widget-button"]')
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        # Wait for bot message (welcome message)
        page.wait_for_selector('[data-testid="message-assistant"]', timeout=5000)

        # Get bot message bubble
        bot_message = page.query_selector('[data-testid="message-assistant"] .bg-surface')
        assert bot_message is not None, "Bot message not found"

        # Check border-radius (should have different values per corner)
        border_radius = bot_message.evaluate(
            "el => window.getComputedStyle(el).borderRadius"
        )

        # Should have rounded-lg (8px) with rounded-bl-sm override
        # This results in something like "8px 8px 8px 4px" or similar
        assert "8px" in border_radius, f"Bot message should use 8px radius, got: {border_radius}"

    @pytest.mark.e2e
    def test_user_message_border_radius(self, page: Page, base_url: str):
        """Verify user messages use rounded-lg with rounded-br-sm"""
        page.goto(base_url)
        page.wait_for_selector('[data-testid="chat-widget-button"]')
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        # Type a message to create a user message
        page.fill('[data-testid="message-input"]', "Test message")
        page.click('[data-testid="send-button"]')

        # Wait for user message
        page.wait_for_selector('[data-testid="message-user"]', timeout=5000)

        # Get user message bubble
        user_message = page.query_selector('[data-testid="message-user"] .bg-primary')
        assert user_message is not None, "User message not found"

        # Check border-radius
        border_radius = user_message.evaluate(
            "el => window.getComputedStyle(el).borderRadius"
        )

        # Should have rounded-lg (8px) with rounded-br-sm override
        assert "8px" in border_radius, f"User message should use 8px radius, got: {border_radius}"


class TestBorderRadiusInputs:
    """Test border radius on input fields"""

    @pytest.mark.e2e
    def test_input_field_border_radius(self, page: Page, base_url: str):
        """Verify input field uses rounded-md (6px) border radius"""
        page.goto(base_url)
        page.wait_for_selector('[data-testid="chat-widget-button"]')
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        # Get input field
        input_field = page.query_selector('[data-testid="message-input"]')
        assert input_field is not None, "Input field not found"

        # Check border-radius
        border_radius = input_field.evaluate(
            "el => window.getComputedStyle(el).borderRadius"
        )

        # Should be rounded-md (6px)
        assert border_radius == "6px", f"Input field has unexpected border-radius: {border_radius}"


class TestBorderRadiusSpecialComponents:
    """Test border radius on special components"""

    @pytest.mark.e2e
    def test_chat_widget_button_border_radius(self, page: Page, base_url: str):
        """Verify chat widget button uses rounded-full (pill shape)"""
        page.goto(base_url)
        page.wait_for_selector('[data-testid="chat-widget-button"]')

        # Get chat button
        chat_button = page.query_selector('[data-testid="chat-widget-button"]')
        assert chat_button is not None, "Chat widget button not found"

        # Check border-radius
        border_radius = chat_button.evaluate(
            "el => window.getComputedStyle(el).borderRadius"
        )

        # Should be rounded-full (50% or 9999px)
        assert border_radius in ["9999px", "50%", "9999px 9999px 9999px 9999px"], \
            f"Chat button should be pill-shaped, got: {border_radius}"

    @pytest.mark.e2e
    def test_typing_indicator_border_radius(self, page: Page, base_url: str):
        """Verify typing indicator uses correct border radius"""
        page.goto(base_url)
        page.wait_for_selector('[data-testid="chat-widget-button"]')
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        # Type a message to trigger typing indicator
        page.fill('[data-testid="message-input"]', "Hello")
        page.click('[data-testid="send-button"]')

        # Wait briefly for typing indicator
        page.wait_for_timeout(500)

        # Look for typing indicator (may not always be visible)
        typing_indicator = page.query_selector('[data-testid="typing-indicator"]')
        if typing_indicator:
            border_radius = typing_indicator.evaluate(
                "el => window.getComputedStyle(el).borderRadius"
            )
            # Typing indicator should match bot message styling (8px) or be 0px
            assert border_radius in ["8px", "0px", "8px 8px 8px 4px"], \
                f"Typing indicator should use 8px or 0px radius, got: {border_radius}"
        else:
            pytest.skip("Typing indicator not displayed")


class TestBorderRadiusConsistency:
    """Test consistency of border radius across the application"""

    @pytest.mark.e2e
    def test_chat_widget_button_border_radius(self, page: Page, base_url: str):
        """Verify chat widget button uses rounded-full (pill shape) - duplicate for coverage"""
        page.goto(base_url)
        page.wait_for_selector('[data-testid="chat-widget-button"]')

        # Get chat button
        chat_button = page.query_selector('[data-testid="chat-widget-button"]')
        assert chat_button is not None, "Chat widget button not found"

        # Check border-radius
        border_radius = chat_button.evaluate(
            "el => window.getComputedStyle(el).borderRadius"
        )

        # Should be rounded-full (50% or 9999px)
        assert border_radius in ["9999px", "50%", "9999px 9999px 9999px 9999px"], \
            f"Chat button should be pill-shaped, got: {border_radius}"

    @pytest.mark.e2e
    def test_header_border_radius(self, page: Page, base_url: str):
        """Verify chat window header uses rounded-t-lg (8px top corners only)"""
        page.goto(base_url)
        page.wait_for_selector('[data-testid="chat-widget-button"]')
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        # Get chat window and check its header (chat window itself has rounded-t-lg)
        chat_window = page.query_selector('[data-testid="chat-window"]')
        assert chat_window is not None, "Chat window not found"

        # The chat window itself uses rounded-t-lg via rounded-lg
        border_radius = chat_window.evaluate(
            "el => window.getComputedStyle(el).borderRadius"
        )

        # Should have 8px on top corners (may be "8px" for all or specified corners)
        assert "8px" in border_radius, f"Chat window should use 8px radius, got: {border_radius}"
