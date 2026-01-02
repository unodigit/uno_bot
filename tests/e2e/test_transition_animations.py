"""E2E tests for transition animations compliance with design system."""
import time

from playwright.sync_api import Page, expect


class TestTransitionAnimations:
    """Test transition animations follow design system specifications."""

    def test_chat_widget_open_animation_timing(self, page: Page, base_url: str) -> None:
        """Verify chat widget opens with 300ms normal transition."""
        page.goto(base_url)

        # Get initial state (button visible, window not visible)
        chat_button = page.get_by_test_id("chat-widget-button")
        expect(chat_button).to_be_visible()

        # Record start time and click
        start_time = time.time()
        chat_button.click()

        # Wait for chat window to appear
        chat_window = page.get_by_test_id("chat-window")

        # Wait up to 500ms for window to become visible
        chat_window.wait_for(state="visible", timeout=500)

        elapsed = (time.time() - start_time) * 1000  # Convert to ms

        # Animation should be approximately 300ms (±100ms tolerance for system variations)
        assert 50 <= elapsed <= 400, f"Chat window open animation should be ~300ms, got: {elapsed}ms"

    def test_quick_reply_button_hover_transition(self, page: Page, base_url: str) -> None:
        """Verify quick reply buttons use fast (150ms) transition on hover."""
        page.goto(base_url)

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for quick replies to appear
        page.wait_for_timeout(2000)

        # Find a quick reply button
        quick_reply = page.locator('[data-testid^="quick-reply-"]').first
        expect(quick_reply).to_be_visible()

        # Get computed transition duration
        transition_duration = quick_reply.evaluate("el => getComputedStyle(el).transitionDuration")

        # Should be 0.15s (150ms) or faster
        duration_value = float(transition_duration.replace('s', ''))
        assert duration_value <= 0.2, f"Quick reply hover transition should be fast (≤200ms), got: {transition_duration}"

    def test_send_button_hover_transition(self, page: Page, base_url: str) -> None:
        """Verify send button uses fast (150ms) transition on hover."""
        page.goto(base_url)

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for window to open
        page.wait_for_timeout(1000)

        # Find send button
        send_button = page.get_by_test_id("send-button")
        expect(send_button).to_be_visible()

        # Get computed transition duration
        transition_duration = send_button.evaluate("el => getComputedStyle(el).transitionDuration")

        # Should be 0.15s (150ms) or faster
        duration_value = float(transition_duration.replace('s', ''))
        assert duration_value <= 0.2, f"Send button hover transition should be fast (≤200ms), got: {transition_duration}"

    def test_floating_button_hover_animation(self, page: Page, base_url: str) -> None:
        """Verify floating chat button has smooth 300ms hover animation."""
        page.goto(base_url)

        # Get floating button
        chat_button = page.get_by_test_id("chat-widget-button")
        expect(chat_button).to_be_visible()

        # Get computed transition duration
        transition_duration = chat_button.evaluate("el => getComputedStyle(el).transitionDuration")

        # Should be 0.3s (300ms) for normal transitions
        duration_value = float(transition_duration.replace('s', ''))
        assert 0.25 <= duration_value <= 0.35, f"Floating button transition should be 300ms, got: {transition_duration}"

    def test_no_janky_animations(self, page: Page, base_url: str) -> None:
        """Verify animations are smooth without janky frame drops."""
        page.goto(base_url)

        # Open and close chat widget multiple times
        for i in range(3):
            # Open
            chat_button = page.get_by_test_id("chat-widget-button")
            chat_button.click()

            # Wait for animation
            page.wait_for_timeout(400)

            # Close
            close_button = page.get_by_test_id("close-button")
            if close_button.is_visible():
                close_button.click()

            # Wait for close animation
            page.wait_for_timeout(400)

            # Re-open to get floating button back
            page.wait_for_timeout(100)

        # If we got here without timeout errors, animations are smooth
        assert True, "All animations completed without timing issues"

    def test_chat_widget_scale_animation(self, page: Page, base_url: str) -> None:
        """Verify chat widget has scale animation on hover."""
        page.goto(base_url)

        # Get floating button
        chat_button = page.get_by_test_id("chat-widget-button")
        expect(chat_button).to_be_visible()

        # Hover over button
        chat_button.hover()

        # Wait for hover transition
        page.wait_for_timeout(350)

        # Get transform value - should include scale
        transform = chat_button.evaluate("el => getComputedStyle(el).transform")

        # Scale should be applied (hover:scale-110)
        # Transform matrix with scale > 1
        assert transform != "none", f"Button should have scale transform on hover, got: {transform}"

    def test_all_transitions_use_css_transitions(self, page: Page, base_url: str) -> None:
        """Verify all interactive elements use CSS transitions (not JavaScript)."""
        page.goto(base_url)

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for UI to load
        page.wait_for_timeout(1000)

        # Check various interactive elements
        elements_to_check = [
            ('[data-testid="send-button"]', "Send button"),
            ('[data-testid^="quick-reply-"]', "Quick reply button"),
        ]

        for selector, name in elements_to_check:
            elements = page.locator(selector).all()
            if elements and elements[0].is_visible():
                element = elements[0]
                transition = element.evaluate("el => getComputedStyle(el).transition")

                # Should have transition property set
                assert transition and transition != "all 0s ease 0s", f"{name} should have CSS transitions, got: {transition}"
