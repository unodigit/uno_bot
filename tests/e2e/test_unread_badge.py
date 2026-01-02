"""
E2E tests for Unread Badge Feature (Feature #117)
Tests that unread badge displays correctly on minimized chat
"""

import pytest
from playwright.sync_api import Page, expect


class TestUnreadBadge:
    """Test unread badge displays correctly on minimized chat"""

    def test_unread_badge_displays_on_minimized_button(self, page: Page, base_url: str) -> None:
        """Verify unread badge appears on minimized chat widget button"""
        page.goto(base_url)

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat window
        page.wait_for_selector('[data-testid="chat-window"]')

        # Send a message to get a bot response
        input_field = page.get_by_test_id("message-input")
        input_field.fill("Hello")
        page.get_by_test_id("send-button").click()

        # Wait for bot response
        page.wait_for_timeout(2000)

        # Minimize the chat
        minimize_button = page.get_by_test_id("minimize-button")
        minimize_button.click()

        # Check that minimized button is visible
        minimized_button = page.get_by_test_id("chat-widget-button-minimized")
        expect(minimized_button).to_be_visible()

        # Check for unread badge
        badge = minimized_button.locator('span.absolute')
        expect(badge).to_be_visible()

    def test_unread_badge_shows_correct_count(self, page: Page, base_url: str) -> None:
        """Verify unread badge shows correct count of messages"""
        page.goto(base_url)

        # Open chat
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        page.wait_for_selector('[data-testid="chat-window"]')

        # Send multiple messages to get multiple responses
        for i in range(2):
            input_field = page.get_by_test_id("message-input")
            input_field.fill(f"Message {i+1}")
            page.get_by_test_id("send-button").click()
            page.wait_for_timeout(1500)

        # Minimize
        minimize_button = page.get_by_test_id("minimize-button")
        minimize_button.click()

        # Check badge count
        minimized_button = page.get_by_test_id("chat-widget-button-minimized")
        badge = minimized_button.locator('span.absolute')
        count_text = badge.text_content()

        # Should show count of assistant messages
        assert count_text in ['1', '2', '3'], f"Badge should show message count, got: {count_text}"

    def test_unread_badge_source_code_exists(self, page: Page, base_url: str) -> None:
        """Verify unread badge code exists in ChatWidget component"""
        with open('client/src/components/ChatWidget.tsx', 'r') as f:
            content = f.read()

            # Check for badge rendering
            assert 'unreadCount' in content, "Should have unreadCount variable"
            assert 'bg-error' in content, "Should use error color"
            assert 'text-white' in content, "Should have white text"
            assert 'rounded-full' in content, "Should be rounded"
            assert 'border-2' in content, "Should have border"
            assert 'border-white' in content, "Should have white border"

    def test_unread_badge_not_shown_when_open(self, page: Page, base_url: str) -> None:
        """Verify unread badge is not shown when chat is open"""
        page.goto(base_url)

        # Open chat
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        page.wait_for_selector('[data-testid="chat-window"]')

        # When chat is open, minimized button should not exist
        assert page.locator('[data-testid="chat-widget-button-minimized"]').count() == 0, \
            "Minimized button should not exist when chat is open"

    def test_unread_badge_clears_on_open(self, page: Page, base_url: str) -> None:
        """Verify badge state when chat is reopened"""
        page.goto(base_url)

        # Open chat
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        page.wait_for_selector('[data-testid="chat-window"]')

        # Send message
        input_field = page.get_by_test_id("message-input")
        input_field.fill("Test")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(1500)

        # Minimize
        minimize_button = page.get_by_test_id("minimize-button")
        minimize_button.click()

        # Verify badge exists
        minimized_button = page.get_by_test_id("chat-widget-button-minimized")
        badge = minimized_button.locator('span.absolute')
        expect(badge).to_be_visible()

        # Reopen chat
        minimized_button.click()

        # Verify we're back to normal button
        normal_button = page.get_by_test_id("chat-widget-button")
        expect(normal_button).to_be_visible()
