"""Playwright fixtures for E2E testing."""
import pytest
from playwright.sync_api import BrowserContext


@pytest.fixture(scope="function")
def browser_context_args(browser_context_args):
    """Configure browser context for E2E tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }


@pytest.fixture(scope="function")
def page(browser: BrowserContext):
    """Create a new page for each test."""
    page = browser.new_page()
    yield page
    page.close()
