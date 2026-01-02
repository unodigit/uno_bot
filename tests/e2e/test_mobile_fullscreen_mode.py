"""E2E tests for mobile full-screen mode feature."""

from playwright.sync_api import Page


class TestMobileFullscreenMode:
    """Test mobile full-screen mode displays correctly on small viewports."""

    def test_mobile_viewport_full_width(self, page: Page):
        """Verify chat takes 100% width on mobile viewport (<768px)."""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 812})

        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Verify mobile responsive classes are applied
        class_attr = chat_window.get_attribute('class')
        assert "sm:w-[95vw]" in class_attr, f"Mobile width class should be applied, got: {class_attr}"

        # Check computed style for mobile width
        chat_element = page.locator('[data-testid="chat-window"]').first
        box = chat_element.bounding_box()

        # On mobile, width should be close to viewport width (95vw)
        viewport_width = 375
        expected_width = viewport_width * 0.95  # 95vw
        assert box['width'] >= expected_width * 0.9, \
            f"Mobile chat width should be ~95vw ({expected_width}), got {box['width']}"

    def test_mobile_viewport_full_height(self, page: Page):
        """Verify chat takes 100% height on mobile viewport (<768px)."""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 812})

        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Verify mobile responsive classes are applied
        class_attr = chat_window.get_attribute('class')
        assert "sm:h-[90vh]" in class_attr, f"Mobile height class should be applied, got: {class_attr}"

        # Check computed style for mobile height
        chat_element = page.locator('[data-testid="chat-window"]').first
        box = chat_element.bounding_box()

        # On mobile, height should be close to viewport height (90vh)
        viewport_height = 812
        expected_height = viewport_height * 0.90  # 90vh
        assert box['height'] >= expected_height * 0.9, \
            f"Mobile chat height should be ~90vh ({expected_height}), got {box['height']}"

    def test_mobile_positioning_correct(self, page: Page):
        """Verify chat positioning is correct on mobile viewport."""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 812})

        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Verify mobile positioning classes are applied
        class_attr = chat_window.get_attribute('class')
        assert "sm:bottom-4" in class_attr, f"Mobile bottom positioning should be applied, got: {class_attr}"
        assert "sm:right-4" in class_attr, f"Mobile right positioning should be applied, got: {class_attr}"

        # Check computed style for mobile positioning
        chat_element = page.locator('[data-testid="chat-window"]').first
        box = chat_element.bounding_box()

        # On mobile, should be positioned near edges with 4px margin
        viewport_width = 375
        viewport_height = 812

        # Check right positioning (should be near right edge with 4px margin)
        expected_right = viewport_width - 4  # 4px from right edge
        assert box['x'] + box['width'] >= expected_right - 10, \
            f"Mobile chat should be positioned near right edge, got x={box['x']}, width={box['width']}"

    def test_mobile_rounded_corners(self, page: Page):
        """Verify chat has proper rounded corners on mobile."""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 812})

        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Verify mobile rounded corner class is applied
        class_attr = chat_window.get_attribute('class')
        assert "sm:rounded-lg" in class_attr, f"Mobile rounded corners should be applied, got: {class_attr}"

    def test_desktop_viewport_different_from_mobile(self, page: Page):
        """Verify desktop viewport has different sizing than mobile."""
        # Set desktop viewport
        page.set_viewport_size({"width": 1024, "height": 768})

        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Verify desktop classes are applied
        class_attr = chat_window.get_attribute('class')
        assert "w-[380px]" in class_attr, f"Desktop width class should be applied, got: {class_attr}"
        assert "h-[520px]" in class_attr, f"Desktop height class should be applied, got: {class_attr}"

        # Check computed style for desktop size
        chat_element = page.locator('[data-testid="chat-window"]').first
        box = chat_element.bounding_box()

        # On desktop, should be fixed size (380x520)
        assert abs(box['width'] - 380) < 10, \
            f"Desktop chat width should be ~380px, got {box['width']}"
        assert abs(box['height'] - 520) < 10, \
            f"Desktop chat height should be ~520px, got {box['height']}"

    def test_responsive_transition(self, page: Page):
        """Verify chat window transitions smoothly between mobile and desktop."""
        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Test multiple viewport sizes
        test_viewports = [
            {"width": 320, "height": 568, "expected_mobile": True},  # Mobile
            {"width": 768, "height": 1024, "expected_mobile": False}, # Tablet
            {"width": 1280, "height": 720, "expected_mobile": False}, # Desktop
        ]

        for viewport in test_viewports:
            page.set_viewport_size(viewport)
            page.wait_for_timeout(100)  # Allow for responsive changes

            class_attr = chat_window.get_attribute('class')

            if viewport["expected_mobile"]:
                # Should have mobile classes
                assert "sm:w-[95vw]" in class_attr, \
                    f"Mobile viewport {viewport['width']}px should have mobile classes, got: {class_attr}"
            else:
                # Should have desktop classes
                assert "w-[380px]" in class_attr, \
                    f"Desktop viewport {viewport['width']}px should have desktop classes, got: {class_attr}"

    def test_mobile_chat_content_fits_properly(self, page: Page):
        """Verify chat content fits properly in mobile full-screen mode."""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 812})

        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Verify header
        header = page.locator('[data-testid="chat-header"]').first
        header.wait_for(timeout=2000)
        assert header.is_visible(), "Header should be visible in mobile mode"

        # Verify messages area
        messages_area = page.locator('[data-testid="messages-area"]').first
        messages_area.wait_for(timeout=2000)
        assert messages_area.is_visible(), "Messages area should be visible in mobile mode"

        # Verify input area
        input_area = page.locator('[data-testid="input-area"]').first
        input_area.wait_for(timeout=2000)
        assert input_area.is_visible(), "Input area should be visible in mobile mode"

    def test_mobile_chat_scrolling_works(self, page: Page):
        """Verify chat scrolling works properly in mobile full-screen mode."""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 812})

        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Send multiple messages to create scrollable content
        input_field = page.get_by_test_id("message-input")
        input_field.wait_for(timeout=5000)

        for i in range(10):
            input_field.fill(f"Test message {i}")
            send_button = page.get_by_test_id("send-button")
            send_button.click()
            page.wait_for_timeout(100)  # Small delay between messages

        # Verify messages area is scrollable
        messages_area = page.locator('[data-testid="messages-area"]').first
        messages_box = messages_area.bounding_box()
        messages_content = page.locator('[data-testid="messages-content"]').first
        content_box = messages_content.bounding_box()

        # Content should be taller than the visible area (scrollable)
        assert content_box['height'] > messages_box['height'], \
            f"Messages content should be scrollable. Content: {content_box['height']}, Visible: {messages_box['height']}"

    def test_mobile_chat_responsive_breakpoints(self, page: Page):
        """Verify chat switches between mobile and desktop modes at correct breakpoints."""
        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Test breakpoint at 640px (sm breakpoint)
        # Below 640px should use mobile styles
        page.set_viewport_size({"width": 639, "height": 800})
        page.wait_for_timeout(100)
        class_attr_small = chat_window.get_attribute('class')

        # Above 640px should use desktop styles
        page.set_viewport_size({"width": 641, "height": 800})
        page.wait_for_timeout(100)
        class_attr_large = chat_window.get_attribute('class')

        # Classes should be different at breakpoint
        assert class_attr_small != class_attr_large, \
            "Classes should change at responsive breakpoint"

        # Small viewport should have mobile classes
        assert "sm:w-[95vw]" in class_attr_small, \
            f"Small viewport should have mobile classes, got: {class_attr_small}"

        # Large viewport should have desktop classes
        assert "w-[380px]" in class_attr_large, \
            f"Large viewport should have desktop classes, got: {class_attr_large}"

    def test_mobile_chat_touch_interactions(self, page: Page):
        """Verify chat interactions work properly in mobile full-screen mode."""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 812})

        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Test touch-friendly button sizes
        send_button = page.get_by_test_id("send-button")
        send_box = send_button.bounding_box()

        # Send button should be large enough for touch (minimum 44x44px recommended)
        assert send_box['width'] >= 40, f"Send button should be touch-friendly, width: {send_box['width']}"
        assert send_box['height'] >= 40, f"Send button should be touch-friendly, height: {send_box['height']}"

        # Test input field accessibility
        input_field = page.get_by_test_id("message-input")
        input_box = input_field.bounding_box()

        # Input field should be accessible and large enough
        assert input_box['height'] >= 40, f"Input field should be accessible, height: {input_box['height']}"

    def test_mobile_chat_performance(self, page: Page):
        """Verify mobile full-screen mode doesn't impact performance."""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 812})

        page.goto("http://localhost:5173")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.wait_for(timeout=10000)
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        chat_window.wait_for(timeout=5000)

        # Measure time to open chat in mobile mode
        import time
        start_time = time.time()

        # Interact with chat elements
        input_field = page.get_by_test_id("message-input")
        input_field.wait_for(timeout=5000)
        input_field.fill("Performance test message")

        send_button = page.get_by_test_id("send-button")
        send_button.click()

        # Wait for response
        page.wait_for_timeout(1000)

        end_time = time.time()
        load_time = end_time - start_time

        # Mobile interactions should be fast (< 2 seconds)
        assert load_time < 2.0, f"Mobile chat interactions should be fast, took {load_time}s"

        # Verify chat window is still visible and functional
        assert chat_window.is_visible(), "Chat window should remain visible after interactions"
