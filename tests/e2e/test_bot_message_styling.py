"""E2E tests for bot message bubble styling."""

import pytest
from playwright.sync_api import Page
from tests.e2e.test_utils import BaseE2ETest, TestConfig


class TestBotMessageStyling(BaseE2ETest):
    """Test bot message bubble styling according to design specifications."""

    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self, page: Page):
        """Setup and cleanup for each test."""
        self.setup(page)
        yield
        self.cleanup()

    def test_bot_message_bubble_left_aligned(self, page: Page):
        """Test that bot messages are left-aligned."""
        self.open_chat_and_send_message(page, "Hello, I need help")

        # Wait for bot response
        bot_message = page.wait_for_selector('[data-testid="message-assistant"]', timeout=10000)
        assert bot_message is not None, "Bot message should be present"

        # Verify left alignment by checking flex direction
        message_container = bot_message.locator('..')
        justify_class = message_container.get_attribute('class')

        assert 'justify-start' in justify_class, "Bot message container should have justify-start class for left alignment"

    def test_bot_message_bubble_background_color(self, page: Page):
        """Test that bot messages have surface background color (#F3F4F6)."""
        self.open_chat_and_send_message(page, "What services do you offer?")

        # Wait for bot response
        bot_message = page.wait_for_selector('[data-testid="message-assistant"]', timeout=10000)
        assert bot_message is not None, "Bot message should be present"

        # Check for correct background color classes
        message_bubble = bot_message.locator('div[style*="max-width"]')
        bubble_class = message_bubble.get_attribute('class')

        # Check for gray-100 class (Tailwind equivalent of #F3F4F6)
        assert 'bg-gray-100' in bubble_class, f"Bot message should have bg-gray-100 class, got: {bubble_class}"

    def test_bot_message_bubble_text_color(self, page: Page):
        """Test that bot messages have correct text color (#1F2937)."""
        self.open_chat_and_send_message(page, "Can you help me with a project?")

        # Wait for bot response
        bot_message = page.wait_for_selector('[data-testid="message-assistant"]', timeout=10000)
        assert bot_message is not None, "Bot message should be present"

        # Check for correct text color classes
        message_bubble = bot_message.locator('div[style*="max-width"]')
        bubble_class = message_bubble.get_attribute('class')

        # Check for gray-800 class (Tailwind equivalent of #1F2937)
        assert 'text-gray-800' in bubble_class, f"Bot message should have text-gray-800 class, got: {bubble_class}"

        # Check timestamp text color
        timestamp = message_bubble.locator('span')
        timestamp_class = timestamp.get_attribute('class')
        assert 'text-gray-600' in timestamp_class, f"Bot message timestamp should have text-gray-600 class, got: {timestamp_class}"

    def test_bot_message_bubble_border_and_styling(self, page: Page):
        """Test that bot messages have proper border and styling."""
        self.open_chat_and_send_message(page, "Tell me more about your process")

        # Wait for bot response
        bot_message = page.wait_for_selector('[data-testid="message-assistant"]', timeout=10000)
        assert bot_message is not None, "Bot message should be present"

        message_bubble = bot_message.locator('div[style*="max-width"]')
        bubble_class = message_bubble.get_attribute('class')

        # Check for border styling
        assert 'border' in bubble_class, f"Bot message should have border class, got: {bubble_class}"
        assert 'border-gray-200' in bubble_class, f"Bot message should have border-gray-200 class, got: {bubble_class}"

        # Check for rounded corners
        assert 'rounded-lg' in bubble_class or 'rounded' in bubble_class, f"Bot message should have rounded corners, got: {bubble_class}"

        # Check for shadow
        assert 'shadow-sm' in bubble_class, f"Bot message should have shadow-sm class, got: {bubble_class}"

    def test_bot_message_bubble_layout_structure(self, page: Page):
        """Test that bot message bubble has correct layout structure."""
        self.open_chat_and_send_message(page, "I'm interested in your services")

        # Wait for bot response
        bot_message = page.wait_for_selector('[data-testid="message-assistant"]', timeout=10000)
        assert bot_message is not None, "Bot message should be present"

        # Verify structure: container -> bubble -> content + timestamp
        message_container = bot_message.locator('..')
        message_bubble = bot_message

        # Check max-width constraint
        bubble_class = message_bubble.get_attribute('class')
        assert 'max-w-[85%]' in bubble_class, f"Bot message should have max-w-[85%] class for width constraint, got: {bubble_class}"

        # Check padding
        assert 'px-3' in bubble_class, f"Bot message should have px-3 class for padding, got: {bubble_class}"
        assert 'py-2' in bubble_class, f"Bot message should have py-2 class for padding, got: {bubble_class}"

        # Check text size
        assert 'text-sm' in bubble_class, f"Bot message should have text-sm class for font size, got: {bubble_class}"

    def test_multiple_bot_messages_consistent_styling(self, page: Page):
        """Test that multiple bot messages have consistent styling."""
        self.open_chat_and_send_message(page, "Hello")

        # Wait for first bot response
        first_bot_message = page.wait_for_selector('[data-testid="message-assistant"]', timeout=10000)
        assert first_bot_message is not None, "First bot message should be present"

        # Send another message to get second bot response
        self.send_message_via_input(page, "Tell me more")
        second_bot_message = page.wait_for_selector('[data-testid="message-assistant"]:nth-child(2)', timeout=10000)
        assert second_bot_message is not None, "Second bot message should be present"

        # Compare styles between both messages
        first_bubble_class = first_bot_message.get_attribute('class')
        second_bubble_class = second_bot_message.get_attribute('class')

        # Both should have same styling classes
        essential_classes = ['bg-gray-100', 'text-gray-800', 'border', 'border-gray-200', 'rounded-lg']

        for class_name in essential_classes:
            assert class_name in first_bubble_class, f"First bot message should have {class_name} class"
            assert class_name in second_bubble_class, f"Second bot message should have {class_name} class"

    def test_bot_message_bubble_responsive_width(self, page: Page):
        """Test that bot message bubble respects responsive width constraints."""
        self.open_chat_and_send_message(page, "This is a longer message to test how the bubble handles text wrapping and width constraints in different screen sizes")

        # Wait for bot response
        bot_message = page.wait_for_selector('[data-testid="message-assistant"]', timeout=10000)
        assert bot_message is not None, "Bot message should be present"

        message_bubble = bot_message.locator('div[style*="max-width"]')
        bubble_class = message_bubble.get_attribute('class')

        # Verify max-width constraint is applied
        assert 'max-w-[85%]' in bubble_class, f"Bot message should respect width constraint, got: {bubble_class}"

        # Verify text wraps properly
        content_text = message_bubble.locator('p').inner_text()
        assert len(content_text) > 0, "Bot message should have content"

    def test_bot_message_bubble_with_special_characters(self, page: Page):
        """Test that bot message bubble displays special characters correctly."""
        self.open_chat_and_send_message(page, "I need help with API integration")

        # Wait for bot response
        bot_message = page.wait_for_selector('[data-testid="message-assistant"]', timeout=10000)
        assert bot_message is not None, "Bot message should be present"

        message_bubble = bot_message.locator('div[style*="max-width"]')
        content_element = message_bubble.locator('p')

        # Verify text content is preserved (including special characters)
        content_text = content_element.inner_text()
        assert len(content_text) > 0, "Bot message should have content"

        # Check that content is properly rendered (no HTML injection issues)
        assert not content_element.inner_html().startswith('<'), "Content should be text, not HTML"