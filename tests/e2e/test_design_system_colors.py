"""
E2E tests for Design System Color Palette (Feature #111)

This test suite verifies the design system color palette is consistently applied
according to the specifications:
- Primary: #2563EB (UnoDigit Blue)
- Primary Dark: #1D4ED8
- Secondary: #10B981 (Success Green)
- Background: #FFFFFF
- Surface: #F3F4F6
- Text: #1F2937
- Text Muted: #6B7280
- Border: #E5E7EB
- Error: #EF4444
"""

import pytest
from playwright.sync_api import Page, expect


class TestDesignSystemColors:
    """Test design system color palette is applied correctly."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment - navigate to chat and open widget."""
        page.goto("http://localhost:5173")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)  # Wait for React to render

    def test_chat_widget_button_has_primary_class(self, page: Page):
        """Verify chat widget button uses primary color class."""
        button = page.locator("[data-testid='chat-widget-button']")
        expect(button).to_be_visible()

        class_attr = button.get_attribute("class")
        assert "bg-primary" in class_attr, "Chat button should have bg-primary class"

    def test_chat_window_header_has_primary_class(self, page: Page):
        """Verify chat window header uses primary color class."""
        # Click to open chat
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

        # Check header
        header = page.locator("[data-testid='chat-window'] header")
        class_attr = header.get_attribute("class")
        assert "bg-primary" in class_attr, "Header should have bg-primary class"

    def test_header_text_has_white_class(self, page: Page):
        """Verify header text is white on primary background."""
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

        header = page.locator("[data-testid='chat-window'] header")
        class_attr = header.get_attribute("class")
        assert "text-white" in class_attr, "Header should have text-white class"

    def test_chat_window_background_white(self, page: Page):
        """Verify chat window has white background class."""
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

        chat_window = page.locator("[data-testid='chat-window']")
        class_attr = chat_window.get_attribute("class")
        assert "bg-white" in class_attr, "Chat window should have bg-white class"

    def test_input_field_has_border_class(self, page: Page):
        """Verify input field uses border color class."""
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

        input_field = page.locator("[data-testid='message-input']")
        class_attr = input_field.get_attribute("class")
        assert "border" in class_attr, "Input field should have border class"

    def test_send_button_has_primary_class(self, page: Page):
        """Verify send button uses primary color class."""
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

        send_button = page.locator("[data-testid='send-button']")
        class_attr = send_button.get_attribute("class")

        # Check for primary color and white text
        assert "bg-primary" in class_attr, "Send button should have bg-primary class"
        assert "text-white" in class_attr, "Send button should have text-white class"

    def test_bot_message_has_surface_class(self, page: Page):
        """Verify bot messages use surface color class."""
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

        # Send a message to get bot response
        page.fill("[data-testid='message-input']", "Hello")
        page.click("[data-testid='send-button']")
        page.wait_for_timeout(2000)

        # Find bot messages
        messages = page.locator("[data-testid^='message-']").all()
        if len(messages) > 1:
            bot_message = messages[0]  # First message is welcome/bot
            class_attr = bot_message.get_attribute("class")
            assert "bg-surface" in class_attr or ("bg-gray" in class_attr and "100" in class_attr), \
                "Bot message should have surface background class"

    def test_bot_message_has_text_color(self, page: Page):
        """Verify bot message text uses text color class."""
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

        page.fill("[data-testid='message-input']", "Test")
        page.click("[data-testid='send-button']")
        page.wait_for_timeout(2000)

        messages = page.locator("[data-testid^='message-']").all()
        if len(messages) > 1:
            bot_message = messages[0]
            class_attr = bot_message.get_attribute("class")
            assert "text-text" in class_attr or ("text-gray" in class_attr and "800" in class_attr), \
                "Bot message should have text color class"

    def test_user_message_has_primary_background(self, page: Page):
        """Verify user messages use primary color background class."""
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

        page.fill("[data-testid='message-input']", "Hello")
        page.click("[data-testid='send-button']")
        page.wait_for_timeout(1000)

        # Last message should be user's
        messages = page.locator("[data-testid^='message-']").all()
        if len(messages) > 0:
            user_message = messages[-1]
            class_attr = user_message.get_attribute("class")
            assert "bg-primary" in class_attr, "User message should have bg-primary class"

    def test_user_message_has_white_text(self, page: Page):
        """Verify user message text is white on primary background."""
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

        page.fill("[data-testid='message-input']", "Test")
        page.click("[data-testid='send-button']")
        page.wait_for_timeout(1000)

        messages = page.locator("[data-testid^='message-']").all()
        if len(messages) > 0:
            user_message = messages[-1]
            class_attr = user_message.get_attribute("class")
            assert "text-white" in class_attr, "User message should have text-white class"

    def test_typing_indicator_has_text_muted_class(self, page: Page):
        """Verify typing indicator uses text-muted color class."""
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

        page.fill("[data-testid='message-input']", "Tell me about your services")
        page.click("[data-testid='send-button']")
        page.wait_for_timeout(1000)

        # Check if typing indicator appears
        typing_dots = page.locator(".animate-bounce")
        if typing_dots.count() > 0:
            class_attr = typing_dots.first.get_attribute("class")
            assert "text-text-muted" in class_attr or ("bg-gray" in class_attr and "600" in class_attr), \
                "Typing indicator should have text-muted color class"

    def test_primary_color_consistency(self, page: Page):
        """Verify primary color class is used consistently."""
        # Collect elements that should be primary-colored
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

        elements_to_check = [
            ("[data-testid='chat-widget-button']", "bg-primary"),
            ("[data-testid='chat-window'] header", "bg-primary"),
            ("[data-testid='send-button']", "bg-primary"),
        ]

        for selector, expected_class in elements_to_check:
            element = page.locator(selector).first
            if element.is_visible():
                class_attr = element.get_attribute("class")
                assert expected_class in class_attr, \
                    f"{selector} should have {expected_class} class"

    def test_surface_color_usage(self, page: Page):
        """Verify surface color class is used where appropriate."""
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

        page.fill("[data-testid='message-input']", "Hello")
        page.click("[data-testid='send-button']")
        page.wait_for_timeout(2000)

        # Check for surface-colored elements
        messages = page.locator("[data-testid^='message-']").all()
        found_surface = False

        for msg in messages[:3]:
            class_attr = msg.get_attribute("class")
            if "bg-surface" in class_attr or ("bg-gray" in class_attr and "100" in class_attr):
                found_surface = True
                break

        assert found_surface, "Should find at least one message with surface background"

    def test_border_color_usage(self, page: Page):
        """Verify border color class is used consistently."""
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

        # Check input field has border
        input_field = page.locator("[data-testid='message-input']")
        class_attr = input_field.get_attribute("class")
        assert "border" in class_attr, "Input field should have border class"

    def test_design_system_classes_present(self, page: Page):
        """Verify key design system classes are present in DOM."""
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

        # Check for various design system classes
        body = page.locator("body")
        html = page.locator("html").inner_html()

        # Should find primary color usage
        assert "bg-primary" in html or "bg-blue-600" in html, \
            "Should use primary color (bg-primary or bg-blue-600)"

        # Should find surface color usage
        assert "bg-surface" in html or "bg-gray-100" in html, \
            "Should use surface color (bg-surface or bg-gray-100)"

        # Should find text color usage
        assert "text-text" in html or "text-gray-800" in html, \
            "Should use text color (text-text or text-gray-800)"
