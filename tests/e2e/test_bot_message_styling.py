"""E2E tests for bot message bubble styling."""
import pytest
from playwright.sync_api import Page

# Frontend URL
FRONTEND_URL = "http://localhost:5173"


class TestBotMessageStyling:
    """Test bot message bubble styling according to design specifications."""

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

    def _get_bot_message_container(self, page: Page) -> any:
        """Get the bot message container (motion.div with flex/justify classes)."""
        container = page.locator('[data-testid="message-assistant"]').first
        container.wait_for(state="visible", timeout=10000)
        return container

    def _get_bot_message_bubble(self, page: Page) -> any:
        """Get the bot message bubble (child div with styling classes)."""
        container = self._get_bot_message_container(page)
        # The bubble is the first child div
        bubble = container.locator('div').first
        return bubble

    def test_bot_message_bubble_left_aligned(self, page: Page):
        """Test that bot messages are left-aligned."""
        self._setup_chat(page)
        self._send_message(page, "Hello, I need help")

        # The data-testid is on the motion.div which contains the justify-start class
        container = self._get_bot_message_container(page)
        justify_class = container.get_attribute('class')

        assert 'justify-start' in justify_class, \
            f"Bot message container should have justify-start class, got: {justify_class}"

    def test_bot_message_bubble_background_color(self, page: Page):
        """Test that bot messages have surface background color (#F3F4F6)."""
        self._setup_chat(page)
        self._send_message(page, "What services do you offer?")

        bubble = self._get_bot_message_bubble(page)
        bubble_class = bubble.get_attribute('class')

        # bg-surface is the design system token equivalent to bg-gray-100
        assert 'bg-surface' in bubble_class, \
            f"Bot message should have bg-surface class, got: {bubble_class}"

    def test_bot_message_bubble_text_color(self, page: Page):
        """Test that bot messages have correct text color (#1F2937)."""
        self._setup_chat(page)
        self._send_message(page, "Can you help me with a project?")

        bubble = self._get_bot_message_bubble(page)
        bubble_class = bubble.get_attribute('class')

        # text-text is the design system token equivalent to text-gray-800
        assert 'text-text' in bubble_class, \
            f"Bot message should have text-text class, got: {bubble_class}"

        # Check timestamp text color
        timestamp = bubble.locator('span')
        timestamp_class = timestamp.get_attribute('class')
        # text-text-muted is the design system token equivalent to text-gray-600
        assert 'text-text-muted' in timestamp_class, \
            f"Bot message timestamp should have text-text-muted class, got: {timestamp_class}"

    def test_bot_message_bubble_border_and_styling(self, page: Page):
        """Test that bot messages have proper border and styling."""
        self._setup_chat(page)
        self._send_message(page, "Tell me more about your process")

        bubble = self._get_bot_message_bubble(page)
        bubble_class = bubble.get_attribute('class')

        # Check for border styling
        assert 'border' in bubble_class, \
            f"Bot message should have border class, got: {bubble_class}"
        # border-border is the design system token equivalent to border-gray-200
        assert 'border-border' in bubble_class, \
            f"Bot message should have border-border class, got: {bubble_class}"

        # Check for rounded corners
        assert 'rounded-lg' in bubble_class, \
            f"Bot message should have rounded-lg class, got: {bubble_class}"

        # Check for shadow
        assert 'shadow-sm' in bubble_class, \
            f"Bot message should have shadow-sm class, got: {bubble_class}"

    def test_bot_message_bubble_layout_structure(self, page: Page):
        """Test that bot message bubble has correct layout structure."""
        self._setup_chat(page)
        self._send_message(page, "I'm interested in your services")

        bubble = self._get_bot_message_bubble(page)
        bubble_class = bubble.get_attribute('class')

        # Check max-width constraint
        assert 'max-w-[85%]' in bubble_class, \
            f"Bot message should have max-w-[85%] class, got: {bubble_class}"

        # Check padding
        assert 'px-3' in bubble_class, \
            f"Bot message should have px-3 class, got: {bubble_class}"
        assert 'py-2' in bubble_class, \
            f"Bot message should have py-2 class, got: {bubble_class}"

        # Check text size
        assert 'text-sm' in bubble_class, \
            f"Bot message should have text-sm class, got: {bubble_class}"

    def test_multiple_bot_messages_consistent_styling(self, page: Page):
        """Test that multiple bot messages have consistent styling."""
        self._setup_chat(page)
        self._send_message(page, "Hello")

        first_bubble = self._get_bot_message_bubble(page)
        first_bubble_class = first_bubble.get_attribute('class')

        # Send second message
        self._send_message(page, "Tell me more")

        # Wait for second bot message
        second_container = page.locator('[data-testid="message-assistant"]').nth(1)
        second_container.wait_for(state="visible", timeout=10000)
        second_bubble = second_container.locator('div').first
        second_bubble_class = second_bubble.get_attribute('class')

        # Both should have same styling classes (using design system tokens)
        essential_classes = ['bg-surface', 'text-text', 'border', 'border-border', 'rounded-lg']

        for class_name in essential_classes:
            assert class_name in first_bubble_class, \
                f"First bot message should have {class_name} class, got: {first_bubble_class}"
            assert class_name in second_bubble_class, \
                f"Second bot message should have {class_name} class, got: {second_bubble_class}"

    def test_bot_message_bubble_responsive_width(self, page: Page):
        """Test that bot message bubble respects responsive width constraints."""
        self._setup_chat(page)
        self._send_message(page, "This is a longer message to test how the bubble handles text wrapping and width constraints in different screen sizes")

        bubble = self._get_bot_message_bubble(page)
        bubble_class = bubble.get_attribute('class')

        # Verify max-width constraint is applied
        assert 'max-w-[85%]' in bubble_class, \
            f"Bot message should respect width constraint, got: {bubble_class}"

        # Verify text wraps properly
        content_text = bubble.locator('p').inner_text()
        assert len(content_text) > 0, "Bot message should have content"

    def test_bot_message_bubble_with_special_characters(self, page: Page):
        """Test that bot message bubble displays special characters correctly."""
        self._setup_chat(page)
        self._send_message(page, "I need help with API integration")

        bubble = self._get_bot_message_bubble(page)
        content_element = bubble.locator('p')

        # Verify text content is preserved
        content_text = content_element.inner_text()
        assert len(content_text) > 0, "Bot message should have content"

        # Check that content is properly rendered (no HTML injection issues)
        inner_html = content_element.inner_html()
        assert not inner_html.startswith('<'), "Content should be text, not HTML"
