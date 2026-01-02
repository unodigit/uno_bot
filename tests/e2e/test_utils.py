"""Utility classes and functions for E2E testing."""
from playwright.sync_api import Page

# Frontend URL
FRONTEND_URL = "http://localhost:5173"


class BaseE2ETest:
    """Base class for E2E tests with common setup and helper methods."""

    def __init__(self):
        self.page = None

    def setup(self, page: Page) -> None:
        """Setup test environment."""
        self.page = page
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

    def cleanup(self) -> None:
        """Cleanup after test."""
        if self.page:
            # Clear any browser storage for clean state
            self.page.evaluate("() => localStorage.clear()")

    def open_chat(self, page: Page) -> None:
        """Open the chat widget."""
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        # Wait for chat window to appear
        page.wait_for_selector('[data-testid="chat-window"]', timeout=5000)

    def send_message_via_input(self, page: Page, message: str) -> None:
        """Send a message via the chat input."""
        input_field = page.get_by_test_id("message-input")
        input_field.fill(message)
        send_button = page.get_by_test_id("send-button")
        send_button.click()

    def open_chat_and_send_message(self, page: Page, message: str) -> None:
        """Open chat and send a message in one step."""
        self.open_chat(page)
        self.send_message_via_input(page, message)


class TestConfig:
    """Configuration for E2E tests."""

    TIMEOUT = 10000  # 10 seconds
    SLOW_MO = 100  # Slow motion in ms
