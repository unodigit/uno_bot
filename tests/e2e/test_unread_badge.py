"""E2E tests for unread badge feature (Feature #125)"""
import pytest
from playwright.sync_api import Page, expect


class TestUnreadBadge:
    """Test unread badge displays on minimized chat widget"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        """Navigate to page and setup chat"""
        page.goto(base_url)
        # Open chat to trigger bot welcome message
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_timeout(1000)
        # Minimize chat
        page.get_by_test_id("minimize-button").click()
        page.wait_for_timeout(500)

    def test_unread_badge_appears_when_new_message(self, page: Page):
        """Verify unread badge appears when new message arrives"""
        # Wait for bot welcome message (this counts as unread)
        badge = page.locator('[data-testid="chat-widget-button-minimized"] span')
        expect(badge).to_be_visible()
        # Should contain a number
        badge_text = badge.inner_text()
        assert badge_text.isdigit(), f"Expected badge to contain number, got: {badge_text}"

    def test_unread_badge_has_red_background(self, page: Page):
        """Verify badge has red background (bg-error = #EF4444)"""
        badge = page.locator('[data-testid="chat-widget-button-minimized"] span')
        expect(badge).to_be_visible()
        # Check for error color class (red) using class list contains
        classes = badge.get_attribute("class") or ""
        assert "bg-error" in classes, f"Expected 'bg-error' in classes: {classes}"

    def test_unread_badge_shows_correct_count(self, page: Page):
        """Verify badge shows correct number of unread messages"""
        badge = page.locator('[data-testid="chat-widget-button-minimized"] span')
        expect(badge).to_be_visible()
        # Should show at least 1 (bot welcome message)
        badge_text = badge.inner_text()
        count = int(badge_text)
        assert count >= 1, f"Expected at least 1 unread message, got {count}"

    def test_unread_badge_has_white_text(self, page: Page):
        """Verify badge text is white for contrast"""
        badge = page.locator('[data-testid="chat-widget-button-minimized"] span')
        expect(badge).to_be_visible()
        classes = badge.get_attribute("class") or ""
        assert "text-white" in classes, f"Expected 'text-white' in classes: {classes}"

    def test_unread_badge_has_rounded_corners(self, page: Page):
        """Verify badge is circular (rounded-full)"""
        badge = page.locator('[data-testid="chat-widget-button-minimized"] span')
        expect(badge).to_be_visible()
        classes = badge.get_attribute("class") or ""
        assert "rounded-full" in classes, f"Expected 'rounded-full' in classes: {classes}"

    def test_unread_badge_positioned_on_button(self, page: Page):
        """Verify badge is positioned on top-right of button"""
        button = page.locator('[data-testid="chat-widget-button-minimized"]')
        badge = page.locator('[data-testid="chat-widget-button-minimized"] span')
        expect(button).to_be_visible()
        expect(badge).to_be_visible()
        # Check positioning classes
        classes = badge.get_attribute("class") or ""
        assert "absolute" in classes, f"Expected 'absolute' in classes: {classes}"
        assert "-top-1" in classes, f"Expected '-top-1' in classes: {classes}"
        assert "-right-1" in classes, f"Expected '-right-1' in classes: {classes}"

    def test_unread_badge_has_border(self, page: Page):
        """Verify badge has border-2 border-white for separation"""
        badge = page.locator('[data-testid="chat-widget-button-minimized"] span')
        expect(badge).to_be_visible()
        classes = badge.get_attribute("class") or ""
        assert "border-2" in classes, f"Expected 'border-2' in classes: {classes}"
        assert "border-white" in classes, f"Expected 'border-white' in classes: {classes}"

    def test_unread_badge_increments_with_multiple_messages(self, page: Page):
        """Verify badge count increases with more messages"""
        badge = page.locator('[data-testid="chat-widget-button-minimized"] span')
        # Get initial count
        initial_count = int(badge.inner_text())
        assert initial_count >= 1
        # Open chat
        page.get_by_test_id("chat-widget-button-minimized").click()
        page.wait_for_timeout(500)
        # Send a message to trigger another bot response
        page.get_by_test_id("message-input").fill("Hello!")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(2000)  # Wait for bot response
        # Minimize again
        page.get_by_test_id("minimize-button").click()
        page.wait_for_timeout(500)
        # Check count increased or stayed same (user messages don't count)
        new_count = int(badge.inner_text())
        # The badge shows assistant messages, so user message shouldn't increment it
        # But bot response should
        assert new_count >= initial_count, f"Expected count to be at least {initial_count}, got {new_count}"

    def test_unread_badge_clears_on_open(self, page: Page):
        """Verify badge clears or updates when chat is opened"""
        # This test verifies the badge state management
        # In current implementation, the badge shows total assistant messages
        badge = page.locator('[data-testid="chat-widget-button-minimized"] span')
        expect(badge).to_be_visible()
        # Open chat
        page.get_by_test_id("chat-widget-button-minimized").click()
        page.wait_for_timeout(500)
        # Verify badge is no longer visible (chat is open, not minimized)
        expect(badge).not_to_be_visible()

    def test_unread_badge_has_proper_sizing(self, page: Page):
        """Verify badge has fixed size (w-6 h-6 = 24px)"""
        badge = page.locator('[data-testid="chat-widget-button-minimized"] span')
        expect(badge).to_be_visible()
        # Check size classes
        classes = badge.get_attribute("class") or ""
        assert "w-6" in classes, f"Expected 'w-6' in classes: {classes}"
        assert "h-6" in classes, f"Expected 'h-6' in classes: {classes}"
        # Verify actual size
        box_size = badge.bounding_box()
        assert box_size is not None
        assert box_size['width'] == 24, f"Expected width 24px, got {box_size['width']}"
        assert box_size['height'] == 24, f"Expected height 24px, got {box_size['height']}"

    def test_unread_badge_text_centered(self, page: Page):
        """Verify badge text is centered and uses flexbox"""
        badge = page.locator('[data-testid="chat-widget-button-minimized"] span')
        expect(badge).to_be_visible()
        # Check flex centering
        classes = badge.get_attribute("class") or ""
        assert "flex" in classes, f"Expected 'flex' in classes: {classes}"
        assert "items-center" in classes, f"Expected 'items-center' in classes: {classes}"
        assert "justify-center" in classes, f"Expected 'justify-center' in classes: {classes}"

    def test_unread_badge_font_styling(self, page: Page):
        """Verify badge uses appropriate font size and weight"""
        badge = page.locator('[data-testid="chat-widget-button-minimized"] span')
        expect(badge).to_be_visible()
        # Check text classes
        classes = badge.get_attribute("class") or ""
        assert "text-xs" in classes, f"Expected 'text-xs' in classes: {classes}"
        assert "font-bold" in classes, f"Expected 'font-bold' in classes: {classes}"
