"""Utility classes and functions for E2E testing."""
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# Frontend URL
FRONTEND_URL = "http://localhost:5173"


def wait_for_element(page: Page, selector: str, timeout: int = 10000):
    """Wait for an element to appear and return it.

    Args:
        page: Playwright page object
        selector: CSS selector to wait for
        timeout: Maximum wait time in milliseconds

    Returns:
        The located element

    Raises:
        TimeoutError: If element doesn't appear within timeout
    """
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return page.locator(selector)
    except PlaywrightTimeoutError:
        raise TimeoutError(f"Element with selector '{selector}' not found within {timeout}ms")


def assert_style_property(page: Page, selector: str, property_name: str, expected_value: str):
    """Assert that an element has a specific style property value.

    Args:
        page: Playwright page object
        selector: CSS selector for the element
        property_name: CSS property name to check
        expected_value: Expected value of the property
    """
    element = page.locator(selector)
    if not element.is_visible():
        raise AssertionError(f"Element '{selector}' is not visible")

    actual_value = element.evaluate(f"el => getComputedStyle(el).{property_name}")
    if actual_value != expected_value:
        raise AssertionError(
            f"Element '{selector}' has {property_name} = {actual_value}, "
            f"expected {expected_value}"
        )


def verify_component_exists(page: Page, selector: str, timeout: int = 5000) -> bool:
    """Verify that a component exists on the page.

    Args:
        page: Playwright page object
        selector: CSS selector for the component
        timeout: Maximum wait time in milliseconds

    Returns:
        True if component exists, False otherwise
    """
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except PlaywrightTimeoutError:
        return False


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
