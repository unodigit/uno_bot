import pytest
from playwright.sync_api import Page, expect


def test_chat_widget_button_visible(page: Page):
    """Test that chat widget button is visible in bottom-right corner"""
    page.goto("http://localhost:5173")
    
    # Wait for page to load
    page.wait_for_load_state("networkidle")
    
    # Check for chat button - it should be a fixed button in bottom-right
    button = page.locator("button.fixed.bottom-6.right-6")
    expect(button).to_be_visible()
    print("Chat widget button is visible")


def test_chat_widget_opens_on_click(page: Page):
    """Test that clicking the button opens the chat window"""
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")
    
    # Click the chat button
    button = page.locator("button.fixed.bottom-6.right-6")
    button.click()
    
    # Check that chat window appears
    chat_window = page.locator("div.fixed.bottom-6.right-6").filter(has_text="UnoBot")
    expect(chat_window).to_be_visible(timeout=3000)
    print("Chat window opens when button clicked")


def test_chat_window_closes(page: Page):
    """Test that minimize button closes the chat window"""
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")
    
    # Open chat
    button = page.locator("button.fixed.bottom-6.right-6")
    button.click()
    
    # Wait for window to appear
    page.wait_for_selector("text=UnoBot", timeout=3000)
    
    # Click close button
    close_button = page.locator("button[aria-label='Close chat']").or_(
        page.locator("button").filter(has=page.locator("svg")).first
    )
    close_button.click()
    
    # Chat window should close, floating button should appear again
    page.wait_for_selector("button.fixed.bottom-6.right-6", state="visible", timeout=3000)
    print("Chat window closes when minimize button clicked")
