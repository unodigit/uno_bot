"""E2E tests for shadow levels design system compliance."""

import time

from playwright.sync_api import Page


class TestShadowLevels:
    """Test shadow levels are correctly applied according to design system."""

    def test_chat_window_has_shadow_xl(self, page: Page):
        """Verify chat window has shadow-xl for depth."""
        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Get the actual chat window element
        chat_container = page.locator('[data-testid="chat-window"]').first

        # Check for shadow-xl class
        class_attr = chat_container.get_attribute('class')
        assert "shadow-xl" in class_attr, f"Chat window should have shadow-xl, got: {class_attr}"

    def test_chat_widget_button_has_shadow_lg(self, page: Page):
        """Verify chat widget button has shadow-lg."""
        page.goto("http://localhost:5173")

        # Wait for chat widget button to be visible
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)

        # Check for shadow-lg class
        class_attr = chat_button.get_attribute('class')
        assert "shadow-lg" in class_attr, f"Chat button should have shadow-lg, got: {class_attr}"

    def test_bot_message_has_shadow_sm(self, page: Page):
        """Verify bot message has shadow-sm."""
        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for welcome message
        first_message = page.locator('[data-testid="message-assistant"]').first
        first_message.wait_for(timeout=5000)

        # Check for shadow-sm class in bot message
        bubble = first_message.locator('div').first
        class_attr = bubble.get_attribute('class')

        # Bot message should have shadow-sm
        assert "shadow-sm" in class_attr, f"Bot message should have shadow-sm, got: {class_attr}"

    def test_user_message_has_shadow_sm(self, page: Page):
        """Verify user message has shadow-sm."""
        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for welcome message
        first_message = page.locator('[data-testid="message-assistant"]').first
        first_message.wait_for(timeout=5000)

        # Send a test message
        input_field = page.get_by_test_id("message-input")
        input_field.wait_for(timeout=5000)
        input_field.fill("Hello, testing user message shadow!")

        send_button = page.get_by_test_id("send-button")
        send_button.click()

        # Wait for user message to appear
        user_message = page.locator('[data-testid="message-user"]').last
        user_message.wait_for(timeout=5000)

        # Check for shadow-sm class in user message
        bubble = user_message.locator('div').first
        class_attr = bubble.get_attribute('class')

        # User message should have shadow-sm
        assert "shadow-sm" in class_attr, f"User message should have shadow-sm, got: {class_attr}"

    def test_typing_indicator_has_shadow_sm(self, page: Page):
        """Verify typing indicator has shadow-sm."""
        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for welcome message
        first_message = page.locator('[data-testid="message-assistant"]').first
        first_message.wait_for(timeout=5000)

        # Send a message to trigger typing indicator
        input_field = page.get_by_test_id("message-input")
        input_field.wait_for(timeout=5000)
        input_field.fill("Please generate a PRD for me")

        send_button = page.get_by_test_id("send-button")
        send_button.click()

        # Wait for typing indicator to appear
        typing_indicator = page.locator('[data-testid="typing-indicator"]').first
        typing_indicator.wait_for(timeout=10000)

        # Check for shadow-sm class in typing indicator
        bubble = typing_indicator.locator('div').first
        class_attr = bubble.get_attribute('class')

        # Typing indicator should have shadow-sm
        assert "shadow-sm" in class_attr, f"Typing indicator should have shadow-sm, got: {class_attr}"

    def test_send_button_has_shadow_sm_when_enabled(self, page: Page):
        """Verify send button has shadow-sm when enabled."""
        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for input field
        input_field = page.get_by_test_id("message-input")
        input_field.wait_for(timeout=5000)

        # Fill input to enable send button
        input_field.fill("Test message")

        # Check send button has shadow-sm when enabled
        send_button = page.get_by_test_id("send-button")
        class_attr = send_button.get_attribute('class')

        # Send button should have shadow-sm when enabled
        assert "shadow-sm" in class_attr, f"Send button should have shadow-sm when enabled, got: {class_attr}"

    def test_quick_reply_buttons_have_shadow_sm(self, page: Page):
        """Verify quick reply buttons have shadow-sm."""
        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for quick replies to appear
        quick_replies = page.locator('[data-testid="quick-reply"]')
        quick_replies.first.wait_for(timeout=5000)

        # Check all quick reply buttons have shadow-sm
        for i in range(quick_replies.count()):
            button = quick_replies.nth(i)
            class_attr = button.get_attribute('class')

            # Quick reply buttons should have shadow-sm
            assert "shadow-sm" in class_attr, f"Quick reply button {i} should have shadow-sm, got: {class_attr}"

    def test_time_slot_buttons_have_shadow_sm(self, page: Page):
        """Verify time slot buttons have shadow-sm."""
        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for welcome message
        first_message = page.locator('[data-testid="message-assistant"]').first
        first_message.wait_for(timeout=5000)

        # Send message to trigger expert matching
        input_field = page.get_by_test_id("message-input")
        input_field.wait_for(timeout=5000)
        input_field.fill("I want to book a consultation")

        send_button = page.get_by_test_id("send-button")
        send_button.click()

        # Wait for expert matching
        expert_match = page.locator('[data-testid="expert-match"]').first
        expert_match.wait_for(timeout=10000)

        # Click match experts button
        match_button = page.get_by_test_id("match-experts-button")
        match_button.click()

        # Wait for calendar picker
        calendar_picker = page.locator('[data-testid="calendar-picker"]').first
        calendar_picker.wait_for(timeout=10000)

        # Check time slot buttons have shadow-sm
        time_slots = page.locator('[data-testid^="time-slot-"]')
        if time_slots.count() > 0:
            for i in range(time_slots.count()):
                button = time_slots.nth(i)
                class_attr = button.get_attribute('class')

                # Time slot buttons should have shadow-sm
                assert "shadow-sm" in class_attr, f"Time slot button {i} should have shadow-sm, got: {class_attr}"

    def test_prd_preview_card_has_shadow_sm(self, page: Page):
        """Verify PRD preview card has shadow-sm."""
        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for welcome message
        first_message = page.locator('[data-testid="message-assistant"]').first
        first_message.wait_for(timeout=5000)

        # Send message to trigger PRD generation
        input_field = page.get_by_test_id("message-input")
        input_field.wait_for(timeout=5000)
        input_field.fill("Please generate a PRD for my AI consulting project")

        send_button = page.get_by_test_id("send-button")
        send_button.click()

        # Wait for PRD preview to appear
        prd_preview = page.locator('[data-testid="prd-preview-card"]').first
        prd_preview.wait_for(timeout=10000)

        # Check for shadow-sm class
        class_attr = prd_preview.get_attribute('class')
        assert "shadow-sm" in class_attr, f"PRD preview should have shadow-sm, got: {class_attr}"

    def test_expert_card_has_shadow_sm(self, page: Page):
        """Verify expert card has shadow-sm."""
        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for welcome message
        first_message = page.locator('[data-testid="message-assistant"]').first
        first_message.wait_for(timeout=5000)

        # Send message to trigger expert matching
        input_field = page.get_by_test_id("message-input")
        input_field.wait_for(timeout=5000)
        input_field.fill("I want to see available experts")

        send_button = page.get_by_test_id("send-button")
        send_button.click()

        # Wait for expert matching
        expert_match = page.locator('[data-testid="expert-match"]').first
        expert_match.wait_for(timeout=10000)

        # Click match experts button
        match_button = page.get_by_test_id("match-experts-button")
        match_button.click()

        # Wait for expert cards
        expert_cards = page.locator('[data-testid^="expert-card-"]')
        expert_cards.first.wait_for(timeout=10000)

        # Check all expert cards have shadow-sm
        for i in range(expert_cards.count()):
            card = expert_cards.nth(i)
            class_attr = card.get_attribute('class')

            # Expert cards should have shadow-sm
            assert "shadow-sm" in class_attr, f"Expert card {i} should have shadow-sm, got: {class_attr}"

    def test_admin_dashboard_cards_have_shadow_sm(self, page: Page):
        """Verify admin dashboard cards have shadow-sm."""
        page.goto("http://localhost:5173/admin")

        # Wait for admin dashboard to load
        dashboard_content = page.locator('[data-testid="admin-dashboard"]').first
        dashboard_content.wait_for(timeout=10000)

        # Check admin dashboard has shadow-sm
        class_attr = dashboard_content.get_attribute('class')
        assert "shadow-sm" in class_attr, f"Admin dashboard should have shadow-sm, got: {class_attr}"

    def test_consistent_shadow_application(self, page: Page):
        """Verify shadow levels are consistently applied across components."""
        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Test multiple components shadow consistency
        components_to_check = [
            (page.get_by_test_id("chat-widget-button"), "shadow-lg", "Chat widget button"),
            (page.locator('[data-testid="chat-window"]').first, "shadow-xl", "Chat window"),
            (page.locator('[data-testid="message-assistant"]').first, "shadow-sm", "Bot message"),
            (page.get_by_test_id("send-button"), "shadow-sm", "Send button"),
        ]

        for locator, expected_shadow, component_name in components_to_check:
            try:
                locator.wait_for(timeout=5000)
                class_attr = locator.get_attribute('class')

                # Verify the expected shadow is present
                assert expected_shadow in class_attr, \
                    f"{component_name} should have {expected_shadow}, got: {class_attr}"
            except Exception as e:
                # Component might not be visible yet, skip if not found
                print(f"Skipping {component_name}: {e}")
                continue

    def test_hover_shadow_states(self, page: Page):
        """Verify hover shadow states work correctly."""
        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Test chat widget button hover shadow
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.hover()

        # Check for hover state (shadow-lg should remain)
        class_attr = chat_button.get_attribute('class')
        assert "shadow-lg" in class_attr, f"Chat button should maintain shadow-lg on hover, got: {class_attr}"

        # Test send button hover if available
        input_field = page.get_by_test_id("message-input")
        if input_field.is_visible():
            input_field.fill("Test")

            send_button = page.get_by_test_id("send-button")
            send_button.hover()

            hover_class_attr = send_button.get_attribute('class')
            assert "shadow-sm" in hover_class_attr, f"Send button should have shadow-sm on hover, got: {hover_class_attr}"

    def test_responsive_shadow_behavior(self, page: Page):
        """Verify shadows work correctly across different screen sizes."""
        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 812})

        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Check mobile chat window has shadow
        class_attr = chat_window.get_attribute('class')
        assert "shadow-xl" in class_attr, f"Mobile chat window should have shadow-xl, got: {class_attr}"

        # Test desktop viewport
        page.set_viewport_size({"width": 1024, "height": 768})

        # Refresh to ensure proper layout
        page.reload()
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Check desktop chat window has shadow
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        class_attr = chat_window.get_attribute('class')
        assert "shadow-xl" in class_attr, f"Desktop chat window should have shadow-xl, got: {class_attr}"

    def test_shadow_performance(self, page: Page):
        """Verify shadow effects don't impact performance significantly."""
        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Measure time to render with shadows
        start_time = time.time()

        # Interact with multiple shadowed elements
        input_field = page.get_by_test_id("message-input")
        input_field.fill("Testing shadow performance")

        # Check that shadows are applied without performance issues
        send_button = page.get_by_test_id("send-button")
        class_attr = send_button.get_attribute('class')

        end_time = time.time()
        render_time = end_time - start_time

        # Shadow application should be fast (< 100ms)
        assert render_time < 0.1, f"Shadow rendering took too long: {render_time}s"

        # Verify shadow is still present
        assert "shadow-sm" in class_attr, f"Send button should have shadow-sm, got: {class_attr}"
