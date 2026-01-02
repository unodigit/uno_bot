"""E2E tests for typing indicator styling and animation."""
from playwright.sync_api import Page

# Frontend URL
FRONTEND_URL = "http://localhost:5173"


class TestTypingIndicatorStyling:
    """Test typing indicator styling and animation according to design specifications."""

    def _setup_chat(self, page: Page) -> None:
        """Navigate to frontend and open chat widget."""
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        page.wait_for_selector('[data-testid="chat-window"]', timeout=5000)

    def _send_message_and_get_typing_indicator(self, page: Page, message: str) -> any:
        """Send a message and return the typing indicator element."""
        input_field = page.get_by_test_id("message-input")
        input_field.fill(message)
        send_button = page.get_by_test_id("send-button")
        send_button.click()

        # Wait for typing indicator to appear
        typing_indicator = page.locator('[data-testid="typing-indicator"]')
        typing_indicator.wait_for(state="visible", timeout=5000)
        return typing_indicator

    def test_typing_indicator_appears_when_bot_is_typing(self, page: Page):
        """Test that typing indicator appears when bot is processing."""
        self._setup_chat(page)

        # Send a message
        typing_indicator = self._send_message_and_get_typing_indicator(page, "Hello")

        # Verify it's visible
        assert typing_indicator.is_visible(), "Typing indicator should be visible"

    def test_typing_indicator_background_color(self, page: Page):
        """Test that typing indicator has surface background color."""
        self._setup_chat(page)
        typing_indicator = self._send_message_and_get_typing_indicator(page, "Hello")

        # Get the bubble element (first child div)
        bubble = typing_indicator.locator('div').first
        bubble_class = bubble.get_attribute('class')

        # Check for surface background
        assert 'bg-surface' in bubble_class, \
            f"Typing indicator should have bg-surface class, got: {bubble_class}"

    def test_typing_indicator_border_styling(self, page: Page):
        """Test that typing indicator has proper border styling."""
        self._setup_chat(page)
        typing_indicator = self._send_message_and_get_typing_indicator(page, "Hello")

        bubble = typing_indicator.locator('div').first
        bubble_class = bubble.get_attribute('class')

        # Check for border
        assert 'border' in bubble_class, \
            f"Typing indicator should have border class, got: {bubble_class}"
        assert 'border-border' in bubble_class, \
            f"Typing indicator should have border-border class, got: {bubble_class}"

    def test_typing_indicator_rounded_corners(self, page: Page):
        """Test that typing indicator has rounded corners."""
        self._setup_chat(page)
        typing_indicator = self._send_message_and_get_typing_indicator(page, "Hello")

        bubble = typing_indicator.locator('div').first
        bubble_class = bubble.get_attribute('class')

        # Check for rounded corners
        assert 'rounded-lg' in bubble_class, \
            f"Typing indicator should have rounded-lg class, got: {bubble_class}"
        assert 'rounded-bl-sm' in bubble_class, \
            f"Typing indicator should have rounded-bl-sm class, got: {bubble_class}"

    def test_typing_indicator_shadow(self, page: Page):
        """Test that typing indicator has shadow."""
        self._setup_chat(page)
        typing_indicator = self._send_message_and_get_typing_indicator(page, "Hello")

        bubble = typing_indicator.locator('div').first
        bubble_class = bubble.get_attribute('class')

        # Check for shadow
        assert 'shadow-sm' in bubble_class, \
            f"Typing indicator should have shadow-sm class, got: {bubble_class}"

    def test_typing_indicator_padding_and_width(self, page: Page):
        """Test that typing indicator has proper padding and max width."""
        self._setup_chat(page)
        typing_indicator = self._send_message_and_get_typing_indicator(page, "Hello")

        bubble = typing_indicator.locator('div').first
        bubble_class = bubble.get_attribute('class')

        # Check padding
        assert 'px-4' in bubble_class, \
            f"Typing indicator should have px-4 class, got: {bubble_class}"
        assert 'py-3' in bubble_class, \
            f"Typing indicator should have py-3 class, got: {bubble_class}"

        # Check max width
        assert 'max-w-[85%]' in bubble_class, \
            f"Typing indicator should have max-w-[85%] class, got: {bubble_class}"

    def test_typing_indicator_dots_structure(self, page: Page):
        """Test that typing indicator has three dots."""
        self._setup_chat(page)
        typing_indicator = self._send_message_and_get_typing_indicator(page, "Hello")

        # Structure: typing-indicator > div (bubble) > div (flex container) > div (dots)
        bubble = typing_indicator.locator('div').first
        flex_container = bubble.locator('div').first
        dots = flex_container.locator('div')

        # Count dots
        dot_count = dots.count()
        assert dot_count == 3, f"Typing indicator should have 3 dots, got {dot_count}"

    def test_typing_indicator_dots_styling(self, page: Page):
        """Test that typing indicator dots have correct styling."""
        self._setup_chat(page)
        typing_indicator = self._send_message_and_get_typing_indicator(page, "Hello")

        # Get the first dot
        bubble = typing_indicator.locator('div').first
        flex_container = bubble.locator('div').first
        dot = flex_container.locator('div').first
        dot_class = dot.get_attribute('class')

        # Check dot styling
        assert 'w-2' in dot_class, f"Dot should have w-2 class, got: {dot_class}"
        assert 'h-2' in dot_class, f"Dot should have h-2 class, got: {dot_class}"
        assert 'bg-text-muted' in dot_class, f"Dot should have bg-text-muted class, got: {dot_class}"
        assert 'rounded-full' in dot_class, f"Dot should have rounded-full class, got: {dot_class}"
        assert 'animate-bounce' in dot_class, f"Dot should have animate-bounce class, got: {dot_class}"

    def test_typing_indicator_dots_animation_delay(self, page: Page):
        """Test that typing indicator dots have staggered animation delays."""
        self._setup_chat(page)
        typing_indicator = self._send_message_and_get_typing_indicator(page, "Hello")

        # Get all dots
        bubble = typing_indicator.locator('div').first
        flex_container = bubble.locator('div').first
        dots = flex_container.locator('div')

        # Check that dots 2 and 3 have animation delays
        second_dot = dots.nth(1)
        third_dot = dots.nth(2)

        second_delay = second_dot.get_attribute('style')
        third_delay = third_dot.get_attribute('style')

        # Second dot should have 0.15s delay
        assert second_delay and '0.15s' in second_delay, \
            f"Second dot should have 0.15s delay, got: {second_delay}"

        # Third dot should have 0.3s delay
        assert third_delay and '0.3s' in third_delay, \
            f"Third dot should have 0.3s delay, got: {third_delay}"

    def test_typing_indicator_left_aligned(self, page: Page):
        """Test that typing indicator is left-aligned (like bot messages)."""
        self._setup_chat(page)
        typing_indicator = self._send_message_and_get_typing_indicator(page, "Hello")

        # The container should have justify-start
        container_class = typing_indicator.get_attribute('class')
        assert 'justify-start' in container_class, \
            f"Typing indicator container should have justify-start class, got: {container_class}"
