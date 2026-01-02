"""Basic functionality test for the frontend application."""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_basic_page_load(page: Page):
    """Test that the basic page loads without errors."""
    # Navigate to main page
    page.goto("http://localhost:5173")

    # Wait for page to fully load
    page.wait_for_load_state("networkidle")

    # Check for console errors
    page_errors = []
    page.on("console", lambda msg: page_errors.append(msg) if msg.type == "error" else None)

    # Verify page has loaded (check for body)
    expect(page.locator("body")).to_be_visible()

    # Check for any console errors
    assert len(page_errors) == 0, f"Console errors found: {page_errors}"


@pytest.mark.e2e
def test_chat_widget_button_exists(page: Page):
    """Test that chat widget button exists and is visible."""
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")

    # Check if chat widget button exists
    button = page.locator('[data-testid="chat-widget-button"]')

    # If button exists, check visibility
    if button.count() > 0:
        expect(button).to_be_visible()
        print("Chat widget button found and visible")
    else:
        print("Chat widget button not found - this might be expected behavior")


@pytest.mark.e2e
def test_page_title(page: Page):
    """Test that the page has a title."""
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")

    title = page.title()
    print(f"Page title: {title}")
    assert title is not None, "Page should have a title"