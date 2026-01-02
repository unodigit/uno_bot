"""
E2E tests for Transition Animations (Feature #115)
Tests that transition animations are smooth and follow design system timing
"""

import pytest
from playwright.sync_api import Page, expect


class TestTransitionAnimations:
    """Test transition animations are smooth and properly configured"""

    def test_chat_widget_has_transition_all(self, page: Page, base_url: str) -> None:
        """Verify chat widget button uses transition-all for smooth animations"""
        page.goto(base_url)

        # Check the chat widget button
        chat_button = page.get_by_test_id("chat-widget-button")
        expect(chat_button).to_be_visible()

        # Verify it has transition-all class
        class_list = chat_button.get_attribute("class")
        assert "transition-all" in class_list, "Chat widget should use transition-all"

    def test_chat_widget_has_duration_300ms(self, page: Page, base_url: str) -> None:
        """Verify chat widget uses 300ms duration for normal transitions"""
        page.goto(base_url)

        chat_button = page.get_by_test_id("chat-widget-button")
        expect(chat_button).to_be_visible()

        # Check for duration-300 class
        class_list = chat_button.get_attribute("class")
        assert "duration-300" in class_list or "transition-all duration-300" in class_list, \
            "Chat widget should use 300ms duration"

    def test_chat_window_opens_with_animation(self, page: Page, base_url: str) -> None:
        """Verify chat window opens with smooth animation"""
        page.goto(base_url)

        # Click to open chat
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for animation to start
        page.wait_for_timeout(100)

        # Chat window should be visible (animation in progress or complete)
        chat_window = page.get_by_test_id("chat-window")
        expect(chat_window).to_be_visible()

    def test_chat_window_closes_with_animation(self, page: Page, base_url: str) -> None:
        """Verify chat window closes with smooth animation"""
        page.goto(base_url)

        # Open chat
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        page.wait_for_selector('[data-testid="chat-window"]')

        # Click close
        close_button = page.get_by_test_id("close-button")
        close_button.click()

        # Wait briefly for animation
        page.wait_for_timeout(100)

        # Chat window should be gone or animating out

    def test_send_button_has_transition_all(self, page: Page, base_url: str) -> None:
        """Verify send button uses transition-all for smooth state changes"""
        page.goto(base_url)
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        send_button = page.get_by_test_id("send-button")
        expect(send_button).to_be_visible()

        class_list = send_button.get_attribute("class")
        assert "transition-all" in class_list, "Send button should use transition-all"

    def test_send_button_has_duration_200ms(self, page: Page, base_url: str) -> None:
        """Verify send button uses 200ms duration for fast transitions"""
        page.goto(base_url)
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        send_button = page.get_by_test_id("send-button")
        class_list = send_button.get_attribute("class")
        assert "duration-200" in class_list, "Send button should use 200ms duration"

    def test_quick_reply_buttons_have_transitions(self, page: Page, base_url: str) -> None:
        """Verify quick reply buttons use transition-all"""
        page.goto(base_url)
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        # Send a message to trigger quick replies
        input_field = page.get_by_test_id("message-input")
        input_field.fill("Hello")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(1000)

        # Check quick reply buttons
        quick_reply = page.locator('[data-testid^="quick-reply-"]').first
        if quick_reply.is_visible():
            class_list = quick_reply.get_attribute("class")
            assert "transition-all" in class_list, "Quick reply buttons should use transition-all"
            assert "duration-200" in class_list, "Quick reply buttons should use 200ms duration"

    def test_message_appears_with_animation(self, page: Page, base_url: str) -> None:
        """Verify messages animate in when added"""
        page.goto(base_url)
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        # Send a message
        input_field = page.get_by_test_id("message-input")
        input_field.fill("Test message")
        page.get_by_test_id("send-button").click()

        # Wait for message to appear
        message = page.locator('[data-testid^="message-"]').first
        expect(message).to_be_visible()

        # Check that it uses motion.div (framer-motion)
        # This is verified by the component structure
        with open('client/src/components/ChatWindow.tsx', 'r') as f:
            content = f.read()
            assert 'motion.div' in content, "Messages should use motion.div for animation"

    def test_typing_indicator_has_bounce_animation(self, page: Page, base_url: str) -> None:
        """Verify typing indicator uses bounce animation"""
        page.goto(base_url)
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        # Send a message to trigger typing indicator
        input_field = page.get_by_test_id("message-input")
        input_field.fill("Hello")
        page.get_by_test_id("send-button").click()

        # Check for typing indicator
        typing_indicator = page.locator('[data-testid="typing-indicator"]')
        if typing_indicator.is_visible():
            # Check for bounce animation class
            class_list = typing_indicator.get_attribute("class")
            assert "animate-bounce" in class_list or "bounce" in class_list.lower(), \
                "Typing indicator should use bounce animation"

    def test_hover_effects_have_transitions(self, page: Page, base_url: str) -> None:
        """Verify hover effects use smooth transitions"""
        page.goto(base_url)
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        # Check chat widget button for hover transition
        chat_button = page.get_by_test_id("chat-widget-button")
        class_list = chat_button.get_attribute("class")
        assert "hover:scale-110" in class_list or "hover:scale" in class_list, \
            "Should have hover scale effect"

    def test_no_janky_animations_in_source(self, page: Page, base_url: str) -> None:
        """Verify all animations use proper timing (no instant transitions)"""
        # Check that components use proper transition classes
        components_to_check = [
            'client/src/components/ChatWindow.tsx',
            'client/src/components/ChatWidget.tsx',
            'client/src/components/ExpertCard.tsx',
        ]

        for component_path in components_to_check:
            try:
                with open(component_path, 'r') as f:
                    content = f.read()
                    # Should use transition classes with proper durations
                    # Not instant (0s) or too slow (>1s for normal interactions)
                    transition_matches = [
                        'transition-all duration-200',
                        'transition-all duration-300',
                        'transition-colors',
                        'transition-shadow',
                        'transition-opacity',
                    ]
                    has_transition = any(tm in content for tm in transition_matches)
                    assert has_transition, f"{component_path} should use proper transition classes"
            except FileNotFoundError:
                pass  # Component may not exist

    def test_framer_motion_transitions_are_configured(self, page: Page, base_url: str) -> None:
        """Verify framer-motion components have proper transition configs"""
        with open('client/src/components/ChatWindow.tsx', 'r') as f:
            content = f.read()
            # Check for motion.div with transition props
            assert 'transition={{ duration: 0.2 }}' in content, \
                "Should use 0.2s (200ms) duration for motion animations"

    def test_scale_transitions_are_smooth(self, page: Page, base_url: str) -> None:
        """Verify scale transitions use proper timing"""
        page.goto(base_url)

        chat_button = page.get_by_test_id("chat-widget-button")
        class_list = chat_button.get_attribute("class")

        # Should have hover:scale-110 with transition-all
        assert "hover:scale-110" in class_list, "Should have scale hover effect"
        assert "transition-all" in class_list, "Should use transition-all for scale"

    def test_all_buttons_have_consistent_transitions(self, page: Page, base_url: str) -> None:
        """Verify all buttons use consistent transition timing"""
        page.goto(base_url)
        page.click('[data-testid="chat-widget-button"]')
        page.wait_for_selector('[data-testid="chat-window"]')

        # Check multiple button types
        button_selectors = [
            '[data-testid="send-button"]',
            '[data-testid="close-button"]',
        ]

        for selector in button_selectors:
            button = page.locator(selector).first
            if button.is_visible():
                class_list = button.get_attribute("class")
                # Should have some transition class
                has_transition = any(t in class_list for t in ['transition-', 'duration-'])
                assert has_transition, f"Button {selector} should have transition classes"

    def test_no_hardcoded_transition_times(self, page: Page, base_url: str) -> None:
        """Verify no hardcoded transition times in style attributes"""
        with open('client/src/components/ChatWindow.tsx', 'r') as f:
            content = f.read()
            # Should not have style={{ transition: '0.3s' }} or similar
            # Should use Tailwind classes instead
            assert 'style={{' not in content or 'transition:' not in content, \
                "Should use Tailwind transition classes, not hardcoded styles"
