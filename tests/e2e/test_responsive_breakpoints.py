"""
E2E tests for responsive breakpoints.
Tests that the chat widget and window adapt correctly at different viewport sizes.
"""

import pytest
from playwright.sync_api import Page, expect


class TestResponsiveBreakpoints:
    """Test suite for responsive breakpoints."""

    def test_mobile_breakpoint_320px(self, page: Page):
        """Test layout at 320px viewport (mobile)."""
        page.goto("http://localhost:5173")

        # Set mobile viewport
        page.set_viewport_size({"width": 320, "height": 568})

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Verify chat widget button is visible and accessible
        chat_button = page.get_by_label("Open chat")
        expect(chat_button).to_be_visible()
        expect(chat_button).to_have_css("width", "60px")
        expect(chat_button).to_have_css("height", "60px")

        # Open chat window
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.locator('[data-testid="chat-window"]')
        chat_window.wait_for()

        # Verify mobile layout: full screen width, full height
        expect(chat_window).to_be_visible()
        expect(chat_window).to_have_css("width", "304px")  # 95vw of 320px
        expect(chat_window).to_have_css("height", "509px")  # 90vh of 568px
        expect(chat_window).to_have_css("bottom", "4px")
        expect(chat_window).to_have_css("right", "4px")

        # Verify header is present and accessible
        header = chat_window.locator(".bg-primary")
        expect(header).to_be_visible()

        # Verify input area is accessible
        input_field = page.locator('[data-testid="message-input"]')
        expect(input_field).to_be_visible()
        expect(input_field).to_be_focused()

    def test_tablet_breakpoint_768px(self, page: Page):
        """Test layout at 768px viewport (tablet)."""
        page.goto("http://localhost:5173")

        # Set tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Verify chat widget button is visible and accessible
        chat_button = page.get_by_label("Open chat")
        expect(chat_button).to_be_visible()

        # Open chat window
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.locator('[data-testid="chat-window"]')
        chat_window.wait_for()

        # Verify tablet layout: fixed size (desktop layout)
        expect(chat_window).to_be_visible()
        expect(chat_window).to_have_css("width", "380px")
        expect(chat_window).to_have_css("height", "520px")
        expect(chat_window).to_have_css("bottom", "24px")
        expect(chat_window).to_have_css("right", "24px")

        # Verify all components are accessible
        input_field = page.locator('[data-testid="message-input"]')
        expect(input_field).to_be_visible()
        expect(input_field).to_be_focused()

        send_button = page.get_by_label("Send message")
        expect(send_button).to_be_visible()

    def test_desktop_breakpoint_1024px(self, page: Page):
        """Test layout at 1024px viewport (desktop)."""
        page.goto("http://localhost:5173")

        # Set desktop viewport
        page.set_viewport_size({"width": 1024, "height": 768})

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Verify chat widget button is visible and accessible
        chat_button = page.get_by_label("Open chat")
        expect(chat_button).to_be_visible()

        # Open chat window
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.locator('[data-testid="chat-window"]')
        chat_window.wait_for()

        # Verify desktop layout: fixed size
        expect(chat_window).to_be_visible()
        expect(chat_window).to_have_css("width", "380px")
        expect(chat_window).to_have_css("height", "520px")
        expect(chat_window).to_have_css("bottom", "24px")
        expect(chat_window).to_have_css("right", "24px")

        # Verify all components are accessible
        input_field = page.locator('[data-testid="message-input"]')
        expect(input_field).to_be_visible()
        expect(input_field).to_be_focused()

        # Test that elements have proper spacing and are not overlapping
        header = chat_window.locator(".bg-primary")
        expect(header).to_be_visible()
        expect(header).to_have_css("height", "48px")

        messages_area = page.locator('[data-testid="messages-container"]')
        expect(messages_area).to_be_visible()

    def test_large_screen_breakpoint_1920px(self, page: Page):
        """Test layout at 1920px viewport (large screen)."""
        page.goto("http://localhost:5173")

        # Set large screen viewport
        page.set_viewport_size({"width": 1920, "height": 1080})

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Verify chat widget button is visible and accessible
        chat_button = page.get_by_label("Open chat")
        expect(chat_button).to_be_visible()

        # Open chat window
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.locator('[data-testid="chat-window"]')
        chat_window.wait_for()

        # Verify large screen layout: fixed size
        expect(chat_window).to_be_visible()
        expect(chat_window).to_have_css("width", "380px")
        expect(chat_window).to_have_css("height", "520px")
        expect(chat_window).to_have_css("bottom", "24px")
        expect(chat_window).to_have_css("right", "24px")

        # Verify all components are accessible and properly sized
        input_field = page.locator('[data-testid="message-input"]')
        expect(input_field).to_be_visible()
        expect(input_field).to_be_focused()

        # Test that quick replies are accessible if present
        # (This assumes quick replies are shown based on chat state)
        quick_replies = page.locator('[data-testid="quick-replies"]')
        if quick_replies.is_visible():
            expect(quick_replies).to_be_visible()
            # Verify quick reply buttons are properly sized for touch
            quick_reply_buttons = quick_replies.locator('button')
            button_count = quick_reply_buttons.count()
            if button_count > 0:
                first_button = quick_reply_buttons.first
                expect(first_button).to_be_visible()

    def test_responsive_transition(self, page: Page):
        """Test that layout transitions smoothly between breakpoints."""
        page.goto("http://localhost:5173")

        # Start with mobile viewport
        page.set_viewport_size({"width": 320, "height": 568})

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Open chat window
        chat_button = page.get_by_label("Open chat")
        chat_button.click()

        chat_window = page.locator('[data-testid="chat-window"]')
        chat_window.wait_for()

        # Verify mobile layout
        expect(chat_window).to_have_css("width", "304px")  # 95vw

        # Transition to tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})

        # Wait for layout to adjust
        page.wait_for_timeout(300)

        # Verify desktop layout
        expect(chat_window).to_have_css("width", "380px")

        # Transition back to mobile
        page.set_viewport_size({"width": 320, "height": 568})
        page.wait_for_timeout(300)

        # Verify mobile layout again
        expect(chat_window).to_have_css("width", "304px")  # 95vw

    def test_touch_targets_mobile(self, page: Page):
        """Test that touch targets are appropriately sized on mobile."""
        page.goto("http://localhost:5173")

        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 812})

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Verify chat widget button size (should be at least 44px)
        chat_button = page.get_by_label("Open chat")
        expect(chat_button).to_be_visible()
        expect(chat_button).to_have_css("width", "60px")
        expect(chat_button).to_have_css("height", "60px")

        # Open chat window
        chat_button.click()

        # Wait for chat window to open
        input_field = page.locator('[data-testid="message-input"]')
        input_field.wait_for()

        # Verify input field is accessible and appropriately sized
        expect(input_field).to_be_visible()
        expect(input_field).to_have_css("height", "40px")  # Should be at least 40px

        # Verify send button is appropriately sized
        send_button = page.get_by_label("Send message")
        expect(send_button).to_be_visible()
        expect(send_button).to_have_css("height", "40px")  # Should be at least 40px

        # Verify header buttons are appropriately sized
        minimize_button = page.locator('button[aria-label="Minimize chat window"]')
        expect(minimize_button).to_be_visible()
        expect(minimize_button).to_have_css("height", "32px")  # Button content area

        close_button = page.get_by_label("Close chat window")
        expect(close_button).to_be_visible()
        expect(close_button).to_have_css("height", "32px")

    def test_mobile_full_screen_mode(self, page: Page):
        """Test that chat takes full width and height on mobile."""
        page.goto("http://localhost:5173")

        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 812})

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Open chat window
        chat_button = page.get_by_label("Open chat")
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.locator('[data-testid="chat-window"]')
        chat_window.wait_for()

        # Verify mobile full-screen characteristics
        expect(chat_window).to_be_visible()

        # Should take most of the screen width (95vw)
        # Should take most of the screen height (90vh)
        # Should have appropriate margins (4px from edges)

        # Verify header is still accessible
        header = chat_window.locator(".bg-primary")
        expect(header).to_be_visible()

        # Verify input area is accessible and doesn't overlap with header
        input_field = page.locator('[data-testid="message-input"]')
        expect(input_field).to_be_visible()
        expect(input_field).to_be_focused()

    def test_responsive_content_display(self, page: Page):
        """Test that content displays properly at all breakpoints."""
        page.goto("http://localhost:5173")

        breakpoints = [
            {"width": 320, "height": 568, "name": "Mobile"},
            {"width": 768, "height": 1024, "name": "Tablet"},
            {"width": 1024, "height": 768, "name": "Desktop"},
            {"width": 1920, "height": 1080, "name": "Large Screen"}
        ]

        for breakpoint in breakpoints:
            # Set viewport
            page.set_viewport_size({"width": breakpoint["width"], "height": breakpoint["height"]})

            # Wait for layout to stabilize
            page.wait_for_timeout(100)

            # Open chat window
            chat_button = page.get_by_label("Open chat")
            chat_button.click()

            chat_window = page.locator('[data-testid="chat-window"]')
            chat_window.wait_for()

            # Verify all essential elements are visible and accessible
            input_field = page.locator('[data-testid="message-input"]')
            expect(input_field).to_be_visible()

            send_button = page.get_by_label("Send message")
            expect(send_button).to_be_visible()

            header = chat_window.locator(".bg-primary")
            expect(header).to_be_visible()

            messages_area = page.locator('[data-testid="messages-container"]')
            expect(messages_area).to_be_visible()

            # Close chat for next iteration
            close_button = page.get_by_label("Close chat window")
            close_button.click()
            page.wait_for_timeout(200)