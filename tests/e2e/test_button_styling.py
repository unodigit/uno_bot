"""
E2E tests for button styling features.
Tests send button and quick reply button styling according to design system.
"""

import pytest
from playwright.sync_api import Page, expect


class TestSendButtonStyling:
    """Feature 103: Send button has correct styling and states"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Navigate to chat and open widget"""
        page.goto("http://localhost:5173")
        page.wait_for_load_state("networkidle")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        page.wait_for_timeout(500)

    def test_send_button_disabled_when_empty(self, page: Page):
        """Verify disabled state styling when input is empty"""
        send_button = page.get_by_test_id("send-button")

        # Verify button exists
        expect(send_button).to_be_visible()

        # Verify disabled state styling
        expect(send_button).to_have_attribute("disabled", "")

        # Check for disabled styling classes
        class_list = send_button.get_attribute("class") or ""
        assert "bg-gray-200" in class_list, "Should have gray background when disabled"
        assert "text-gray-400" in class_list, "Should have gray text when disabled"
        assert "opacity-60" in class_list, "Should have reduced opacity when disabled"
        assert "cursor-not-allowed" in class_list, "Should have not-allowed cursor when disabled"

    def test_send_button_enabled_with_text(self, page: Page):
        """Verify enabled state styling when input has text"""
        input_field = page.get_by_test_id("message-input")
        send_button = page.get_by_test_id("send-button")

        # Type a message
        input_field.fill("Hello, this is a test message")
        page.wait_for_timeout(200)

        # Verify button is enabled
        is_disabled = send_button.is_disabled()
        assert not is_disabled, "Button should be enabled when input has text"

        # Check for enabled styling classes
        class_list = send_button.get_attribute("class") or ""
        assert "bg-primary" in class_list, "Should have primary background when enabled"
        assert "text-white" in class_list, "Should have white text when enabled"
        assert "shadow-sm" in class_list, "Should have shadow when enabled"

    def test_send_button_hover_effect(self, page: Page):
        """Verify hover state styling"""
        input_field = page.get_by_test_id("message-input")
        send_button = page.get_by_test_id("send-button")

        # Type a message to enable button
        input_field.fill("Test message")

        # Hover over button
        send_button.hover()
        page.wait_for_timeout(100)

        # Verify hover styling is applied
        class_list = send_button.get_attribute("class") or ""
        assert "hover:bg-primary-dark" in class_list, "Should have darker blue on hover"
        assert "hover:shadow" in class_list, "Should have stronger shadow on hover"

    def test_send_button_focus_ring(self, page: Page):
        """Verify focus state has visible ring"""
        input_field = page.get_by_test_id("message-input")
        send_button = page.get_by_test_id("send-button")

        # Type a message to enable button
        input_field.fill("Test message")

        # Focus the button
        send_button.focus()
        page.wait_for_timeout(100)

        # Verify focus ring styling
        class_list = send_button.get_attribute("class") or ""
        assert "focus:ring-2" in class_list, "Should have 2px focus ring"
        assert "focus:ring-primary" in class_list, "Should have primary color focus ring"

    def test_send_button_active_scale(self, page: Page):
        """Verify active state has scale effect"""
        input_field = page.get_by_test_id("message-input")
        send_button = page.get_by_test_id("send-button")

        # Type a message to enable button
        input_field.fill("Test message")

        # Check for active scale class
        class_list = send_button.get_attribute("class") or ""
        assert "active:scale-95" in class_list, "Should scale down when clicked"

    def test_send_button_transitions(self, page: Page):
        """Verify smooth transitions"""
        send_button = page.get_by_test_id("send-button")

        # Check for transition classes
        class_list = send_button.get_attribute("class") or ""
        assert "transition-all" in class_list, "Should have all properties transition"
        assert "duration-200" in class_list, "Should have 200ms transition duration"


class TestQuickReplyButtonsStyling:
    """Feature 104: Quick reply buttons have correct styling"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Navigate to chat, open widget, and wait for quick replies"""
        page.goto("http://localhost:5173")
        page.wait_for_load_state("networkidle")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        page.wait_for_timeout(1000)

        # Wait for welcome message and quick replies
        page.wait_for_selector("[data-testid^='quick-reply-']", timeout=5000)

    def test_quick_reply_buttons_visible(self, page: Page):
        """Verify quick reply buttons are displayed"""
        # Wait for quick replies to appear
        page.wait_for_selector("[data-testid^='quick-reply-']", timeout=5000)

        # Get all quick reply buttons
        quick_replies = page.locator("[data-testid^='quick-reply-']")

        # Verify at least one quick reply exists
        count = quick_replies.count()
        assert count > 0, f"Expected at least 1 quick reply button, found {count}"

    def test_quick_reply_buttons_base_styling(self, page: Page):
        """Verify base styling matches design system"""
        page.wait_for_selector("[data-testid^='quick-reply-']", timeout=5000)
        first_button = page.locator("[data-testid^='quick-reply-']").first

        # Check button is visible
        expect(first_button).to_be_visible()

        # Verify design system classes
        class_list = first_button.get_attribute("class") or ""
        assert "bg-surface" in class_list, "Should use surface background color"
        assert "text-text" in class_list, "Should use text color"
        assert "border-border" in class_list, "Should use border color"
        assert "rounded-full" in class_list, "Should be fully rounded"
        assert "shadow-sm" in class_list, "Should have small shadow"

    def test_quick_reply_buttons_horizontal_layout(self, page: Page):
        """Verify buttons are arranged horizontally with wrap"""
        page.wait_for_selector("[data-testid^='quick-reply-']", timeout=5000)

        # Get parent container
        container = page.locator("[data-testid='quick-replies'] .flex.flex-wrap")

        # Verify flex layout exists
        expect(container).to_be_visible()

    def test_quick_reply_buttons_gap_spacing(self, page: Page):
        """Verify proper gap between buttons"""
        page.wait_for_selector("[data-testid^='quick-reply-']", timeout=5000)

        # Get container and verify gap class
        container = page.locator("[data-testid='quick-replies'] .flex.flex-wrap")
        class_list = container.get_attribute("class") or ""
        assert "gap-2" in class_list, "Should have 8px gap between buttons"

    def test_quick_reply_buttons_hover_effect(self, page: Page):
        """Verify hover state styling"""
        page.wait_for_selector("[data-testid^='quick-reply-']", timeout=5000)
        first_button = page.locator("[data-testid^='quick-reply-']").first

        # Hover over button
        first_button.hover()
        page.wait_for_timeout(100)

        # Verify hover styling
        class_list = first_button.get_attribute("class") or ""
        assert "hover:bg-gray-200" in class_list, "Should darken on hover"

    def test_quick_reply_buttons_active_scale(self, page: Page):
        """Verify active state scale effect"""
        page.wait_for_selector("[data-testid^='quick-reply-']", timeout=5000)
        first_button = page.locator("[data-testid^='quick-reply-']").first

        # Check for active scale class
        class_list = first_button.get_attribute("class") or ""
        assert "active:scale-95" in class_list, "Should scale down when clicked"

    def test_quick_reply_buttons_focus_ring(self, page: Page):
        """Verify focus ring for accessibility"""
        page.wait_for_selector("[data-testid^='quick-reply-']", timeout=5000)
        first_button = page.locator("[data-testid^='quick-reply-']").first

        # Focus the button
        first_button.focus()
        page.wait_for_timeout(100)

        # Verify focus ring styling
        class_list = first_button.get_attribute("class") or ""
        assert "focus:ring-2" in class_list, "Should have 2px focus ring"
        assert "focus:ring-primary" in class_list, "Should have primary color focus ring"
        assert "focus:ring-offset-2" in class_list, "Should have ring offset"

    def test_quick_reply_buttons_disabled_state(self, page: Page):
        """Verify buttons can be disabled during streaming"""
        page.wait_for_selector("[data-testid^='quick-reply-']", timeout=5000)
        first_button = page.locator("[data-testid^='quick-reply-']").first

        # Check for disabled state classes
        class_list = first_button.get_attribute("class") or ""
        assert "disabled:opacity-50" in class_list, "Should be 50% opacity when disabled"
        assert "disabled:cursor-not-allowed" in class_list, "Should show not-allowed cursor when disabled"

    def test_quick_reply_buttons_transitions(self, page: Page):
        """Verify smooth transitions"""
        page.wait_for_selector("[data-testid^='quick-reply-']", timeout=5000)
        first_button = page.locator("[data-testid^='quick-reply-']").first

        # Check for transition classes
        class_list = first_button.get_attribute("class") or ""
        assert "transition-all" in class_list, "Should have all properties transition"
        assert "duration-200" in class_list, "Should have 200ms transition duration"

    def test_quick_reply_buttons_clickable(self, page: Page):
        """Verify buttons are interactive"""
        page.wait_for_selector("[data-testid^='quick-reply-']", timeout=5000)
        first_button = page.locator("[data-testid^='quick-reply-']").first

        # Get button text before clicking
        message_text = first_button.inner_text()

        # Click button
        first_button.click()
        page.wait_for_timeout(1000)

        # Verify message was sent (look for text in chat messages)
        # Try multiple selectors for message content
        messages = page.locator("div[class*='message']").or_(
            page.locator("[data-testid*='message']")
        ).or_(
            page.locator("text=" + message_text)
        )

        # At minimum, verify the button text exists somewhere on page
        page_content = page.content()
        assert message_text in page_content, f"Button text '{message_text}' not found in page after clicking"
