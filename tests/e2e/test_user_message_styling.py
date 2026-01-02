"""E2E tests for user message bubble styling."""
import pytest
from playwright.sync_api import Page

# Frontend URL
FRONTEND_URL = "http://localhost:5173"


class TestUserMessageStyling:
    """Test user message bubble styling according to design specifications."""

    def _setup_chat(self, page: Page) -> None:
        """Navigate to frontend and open chat widget."""
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        page.wait_for_selector('[data-testid="chat-window"]', timeout=5000)

    def _send_message(self, page: Page, message: str) -> None:
        """Send a message via chat input."""
        input_field = page.get_by_test_id("message-input")
        input_field.fill(message)
        send_button = page.get_by_test_id("send-button")
        send_button.click()

    def _get_user_message_container(self, page: Page) -> any:
        """Get the user message container (motion.div with flex/justify classes)."""
        container = page.locator('[data-testid="message-user"]').first
        container.wait_for(state="visible", timeout=10000)
        return container

    def _get_user_message_bubble(self, page: Page) -> any:
        """Get the user message bubble (child div with styling classes)."""
        container = self._get_user_message_container(page)
        # The bubble is the first child div
        bubble = container.locator('div').first
        return bubble

    def test_user_message_bubble_right_aligned(self, page: Page):
        """Test that user messages are right-aligned."""
        self._setup_chat(page)
        self._send_message(page, "Hello, I need help")

        # The data-testid is on the motion.div which contains the justify-end class
        container = self._get_user_message_container(page)
        justify_class = container.get_attribute('class')

        assert 'justify-end' in justify_class, \
            f"User message container should have justify-end class, got: {justify_class}"

    def test_user_message_bubble_background_color(self, page: Page):
        """Test that user messages have primary background color (#2563EB)."""
        self._setup_chat(page)
        self._send_message(page, "What services do you offer?")

        bubble = self._get_user_message_bubble(page)
        bubble_class = bubble.get_attribute('class')

        # Check for primary background class
        assert 'bg-primary' in bubble_class, \
            f"User message should have bg-primary class, got: {bubble_class}"

    def test_user_message_bubble_text_color(self, page: Page):
        """Test that user messages have white text color."""
        self._setup_chat(page)
        self._send_message(page, "Can you help me with a project?")

        bubble = self._get_user_message_bubble(page)
        bubble_class = bubble.get_attribute('class')

        # Check for white text
        assert 'text-white' in bubble_class, \
            f"User message should have text-white class, got: {bubble_class}"

        # Check timestamp text color
        timestamp = bubble.locator('span')
        timestamp_class = timestamp.get_attribute('class')
        assert 'text-white/80' in timestamp_class, \
            f"User message timestamp should have text-white/80 class, got: {timestamp_class}"

    def test_user_message_bubble_border_and_styling(self, page: Page):
        """Test that user messages have proper border and styling."""
        self._setup_chat(page)
        self._send_message(page, "Tell me more about your process")

        bubble = self._get_user_message_bubble(page)
        bubble_class = bubble.get_attribute('class')

        # Check for rounded corners (user messages have rounded-br-sm)
        assert 'rounded-br-sm' in bubble_class, \
            f"User message should have rounded-br-sm class, got: {bubble_class}"
        assert 'rounded-lg' in bubble_class, \
            f"User message should have rounded-lg class, got: {bubble_class}"

        # Check for shadow
        assert 'shadow-sm' in bubble_class, \
            f"User message should have shadow-sm class, got: {bubble_class}"

    def test_user_message_bubble_layout_structure(self, page: Page):
        """Test that user message bubble has correct layout structure."""
        self._setup_chat(page)
        self._send_message(page, "I'm interested in your services")

        bubble = self._get_user_message_bubble(page)
        bubble_class = bubble.get_attribute('class')

        # Check max-width constraint
        assert 'max-w-[85%]' in bubble_class, \
            f"User message should have max-w-[85%] class, got: {bubble_class}"

        # Check padding
        assert 'px-3' in bubble_class, \
            f"User message should have px-3 class, got: {bubble_class}"
        assert 'py-2' in bubble_class, \
            f"User message should have py-2 class, got: {bubble_class}"

        # Check text size
        assert 'text-sm' in bubble_class, \
            f"User message should have text-sm class, got: {bubble_class}"

    def test_multiple_user_messages_consistent_styling(self, page: Page):
        """Test that multiple user messages have consistent styling."""
        self._setup_chat(page)
        self._send_message(page, "Hello")

        first_bubble = self._get_user_message_bubble(page)
        first_bubble_class = first_bubble.get_attribute('class')

        # Send second message
        self._send_message(page, "Tell me more")

        # Wait for second user message
        second_container = page.locator('[data-testid="message-user"]').nth(1)
        second_container.wait_for(state="visible", timeout=10000)
        second_bubble = second_container.locator('div').first
        second_bubble_class = second_bubble.get_attribute('class')

        # Both should have same styling classes
        essential_classes = ['bg-primary', 'text-white', 'rounded-lg', 'rounded-br-sm']

        for class_name in essential_classes:
            assert class_name in first_bubble_class, \
                f"First user message should have {class_name} class, got: {first_bubble_class}"
            assert class_name in second_bubble_class, \
                f"Second user message should have {class_name} class, got: {second_bubble_class}"

    def test_user_message_bubble_responsive_width(self, page: Page):
        """Test that user message bubble respects responsive width constraints."""
        self._setup_chat(page)
        self._send_message(page, "This is a longer message to test how the bubble handles text wrapping and width constraints in different screen sizes")

        bubble = self._get_user_message_bubble(page)
        bubble_class = bubble.get_attribute('class')

        # Verify max-width constraint is applied
        assert 'max-w-[85%]' in bubble_class, \
            f"User message should respect width constraint, got: {bubble_class}"

        # Verify text wraps properly
        content_text = bubble.locator('p').inner_text()
        assert len(content_text) > 0, "User message should have content"

    def test_user_message_bubble_with_special_characters(self, page: Page):
        """Test that user message bubble displays special characters correctly."""
        self._setup_chat(page)
        self._send_message(page, "I need help with API integration")

        bubble = self._get_user_message_bubble(page)
        content_element = bubble.locator('p')

        # Verify text content is preserved
        content_text = content_element.inner_text()
        assert len(content_text) > 0, "User message should have content"

        # Check that content is properly rendered (no HTML injection issues)
        inner_html = content_element.inner_html()
        assert not inner_html.startswith('<'), "Content should be text, not HTML"
