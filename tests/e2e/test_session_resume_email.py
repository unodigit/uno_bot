"""E2E tests for session resume via email link functionality."""

import pytest
from playwright.async_api import Page, expect


@pytest.mark.asyncio
async def test_session_resume_via_email_link(page: Page):
    """Test that session can be resumed via email link with session_id parameter."""

    # Step 1: Start conversation and get session ID
    await page.goto("http://localhost:5180")
    await page.wait_for_load_state("networkidle")

    # Open chat widget
    chat_button = page.get_by_test_id("chat-widget-button")
    await chat_button.click()

    # Wait for chat to open and initial message
    await page.wait_for_selector('[data-testid="chat-messages"]')
    await expect(page.locator('[data-testid="chat-messages"]')).to_be_visible()

    # Get session ID from localStorage
    session_id = await page.evaluate("localStorage.getItem('unobot_session_id')")
    assert session_id is not None, "Session should be created automatically"
    print(f"Created session ID: {session_id}")

    # Step 2: Exchange a few messages to establish conversation
    message_input = page.get_by_placeholder("Type your message...")
    await message_input.fill("Hi, I need help with a business consultation.")
    await message_input.press("Enter")

    # Wait for bot response
    await page.wait_for_timeout(2000)  # Wait for streaming response

    # Send another message
    await message_input.fill("Can you tell me about your services?")
    await message_input.press("Enter")

    await page.wait_for_timeout(2000)  # Wait for response

    # Step 3: Get session resume URL
    resume_url = await page.evaluate(f"window.location.origin + '?session_id={session_id}'")
    print(f"Session resume URL: {resume_url}")

    # Step 4: Close browser completely (simulate user closing browser)
    await page.close()

    # Create new page to simulate fresh browser session
    new_page = await page.context.browser.new_page()

    # Step 5: Open email link with session ID
    await new_page.goto(resume_url)
    await new_page.wait_for_load_state("networkidle")

    # Step 6: Verify conversation is resumed
    new_session_id = await new_page.evaluate("localStorage.getItem('unobot_session_id')")
    assert new_session_id == session_id, "Session ID should be the same"

    # Step 7: Verify full history is visible
    await new_page.wait_for_selector('[data-testid="chat-widget-button"]')
    chat_button = new_page.get_by_test_id("chat-widget-button")
    await chat_button.click()

    # Wait for chat to open
    await new_page.wait_for_selector('[data-testid="chat-messages"]')
    await expect(new_page.locator('[data-testid="chat-messages"]')).to_be_visible()

    # Check that messages are present (should have more than just the welcome message)
    message_elements = await new_page.locator('[data-testid="chat-messages"] .message-bubble').all()
    assert len(message_elements) >= 4, f"Should have multiple messages, found {len(message_elements)}"

    print(f"Verified {len(message_elements)} messages in resumed session")

    # Verify one of our messages is present
    message_text = await message_elements[0].inner_text()
    assert "business consultation" in message_text or "services" in message_text or "Hello" in message_text, \
        f"Should contain user message content: {message_text}"

    await new_page.close()


@pytest.mark.asyncio
async def test_session_resume_url_parameter_handling(page: Page):
    """Test that session ID in URL parameter is properly handled."""

    # Create a test session ID
    test_session_id = "test-session-123"

    # Navigate to URL with session_id parameter
    test_url = f"http://localhost:5180?session_id={test_session_id}"
    await page.goto(test_url)
    await page.wait_for_load_state("networkidle")

    # Verify session ID is stored in localStorage
    stored_session_id = await page.evaluate("localStorage.getItem('unobot_session_id')")
    assert stored_session_id == test_session_id, \
        f"Expected {test_session_id}, got {stored_session_id}"

    print(f"Successfully stored session ID: {stored_session_id}")


@pytest.mark.asyncio
async def test_session_resume_without_parameter(page: Page):
    """Test that normal session creation works when no session_id parameter is provided."""

    # Navigate to root URL without session_id parameter
    await page.goto("http://localhost:5180")
    await page.wait_for_load_state("networkidle")

    # Session ID should be null initially
    initial_session_id = await page.evaluate("localStorage.getItem('unobot_session_id')")
    assert initial_session_id is None, "No session should exist initially"

    # Open chat to create new session
    chat_button = page.get_by_test_id("chat-widget-button")
    await chat_button.click()

    # Wait for session to be created
    await page.wait_for_timeout(1000)

    # Now session should be created
    created_session_id = await page.evaluate("localStorage.getItem('unobot_session_id')")
    assert created_session_id is not None, "Session should be created when chat is opened"

    print(f"New session created: {created_session_id}")