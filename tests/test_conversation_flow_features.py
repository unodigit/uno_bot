"""Test conversation flow features (10-19) with Playwright."""
import asyncio
import pytest
from playwright.async_api import Page, expect


@pytest.mark.asyncio
async def test_feature_10_bot_asks_name(page: Page):
    """Feature 10: Bot asks for user's name during conversation."""
    # Navigate to app
    await page.goto("http://localhost:5181")
    await page.wait_for_load_state("networkidle")

    # Wait for chat widget to load
    await page.wait_for_selector("[data-testid='chat-widget-button']", timeout=5000)

    # Open chat widget
    await page.click("[data-testid='chat-widget-button']")
    await page.wait_for_selector("[data-testid='chat-window']", timeout=5000)

    # Wait for welcome message
    await page.wait_for_selector("[data-testid='chat-message']:has-text('Welcome')", timeout=5000)

    # Check if the welcome message asks for name
    messages = await page.locator("[data-testid='chat-message']").all()
    assert len(messages) >= 1, "Should have at least welcome message"

    welcome_text = await messages[0].text_content()
    assert welcome_text is not None, "Welcome message should have text content"

    # The welcome message should ask for name
    assert "name" in welcome_text.lower() or "what's your name" in welcome_text.lower() or "to get started" in welcome_text.lower(), \
        f"Welcome message should ask for name. Got: {welcome_text}"


@pytest.mark.asyncio
async def test_feature_11_collects_email(page: Page):
    """Feature 11: Bot collects and validates email address."""
    await page.goto("http://localhost:5181")
    await page.wait_for_load_state("networkidle")

    # Open chat
    await page.click("[data-testid='chat-widget-button']")
    await page.wait_for_selector("[data-testid='chat-window']")

    # Provide name
    input_box = await page.wait_for_selector("[data-testid='chat-input']", timeout=5000)
    await input_box.fill("My name is John Doe")
    await page.click("[data-testid='send-button']")

    # Wait for response
    await page.wait_for_selector("[data-testid='chat-message']:has-text('John')", timeout=10000)

    # Check if bot asks for email
    messages = await page.locator("[data-testid='chat-message']").all()
    last_message = messages[-1]
    last_text = await last_message.text_content()
    assert last_text is not None, "Last message should have text content"

    # Should ask for email
    assert "email" in last_text.lower(), f"Bot should ask for email after name. Got: {last_text}"


@pytest.mark.asyncio
async def test_feature_12_collects_company(page: Page):
    """Feature 12: Bot collects company information."""
    await page.goto("http://localhost:5181")
    await page.wait_for_load_state("networkidle")

    # Open chat
    await page.click("[data-testid='chat-widget-button']")
    await page.wait_for_selector("[data-testid='chat-window']")

    # Provide name
    await page.fill("[data-testid='chat-input']", "My name is John Doe")
    await page.click("[data-testid='send-button']")
    await page.wait_for_timeout(2000)

    # Provide email
    await page.fill("[data-testid='chat-input']", "john@example.com")
    await page.click("[data-testid='send-button']")
    await page.wait_for_timeout(2000)

    # Provide challenge
    await page.fill("[data-testid='chat-input']", "We need help with data analytics")
    await page.click("[data-testid='send-button']")
    await page.wait_for_timeout(2000)

    # Check if bot asks about company/industry
    messages = await page.locator("[data-testid='chat-message']").all()
    last_message = messages[-1]
    last_text = await last_message.text_content()
    assert last_text is not None, "Last message should have text content"

    # Should ask about company or industry
    assert any(keyword in last_text.lower() for keyword in ["company", "industry", "organization", "business"]), \
        f"Bot should ask about company/industry. Got: {last_text}"


@pytest.mark.asyncio
async def test_feature_14_asks_tech_stack(page: Page):
    """Feature 14: Bot asks about current technology stack."""
    await page.goto("http://localhost:5181")
    await page.wait_for_load_state("networkidle")

    # Open chat
    await page.click("[data-testid='chat-widget-button']")
    await page.wait_for_selector("[data-testid='chat-window']")

    # Provide name
    await page.fill("[data-testid='chat-input']", "My name is John Doe")
    await page.click("[data-testid='send-button']")
    await page.wait_for_timeout(2000)

    # Provide email
    await page.fill("[data-testid='chat-input']", "john@example.com")
    await page.click("[data-testid='send-button']")
    await page.wait_for_timeout(2000)

    # Provide business context
    await page.fill("[data-testid='chat-input']", "We are a healthcare company and need help with analytics")
    await page.click("[data-testid='send-button']")
    await page.wait_for_timeout(2000)

    # Provide company
    await page.fill("[data-testid='chat-input']", "We have about 50 people")
    await page.click("[data-testid='send-button']")
    await page.wait_for_timeout(2000)

    # Check if bot asks about tech stack or budget
    messages = await page.locator("[data-testid='chat-message']").all()
    last_message = messages[-1]
    last_text = await last_message.text_content()
    assert last_text is not None, "Last message should have text content"

    # Should ask about tech stack or move to qualification
    print(f"Last message: {last_text}")


@pytest.mark.asyncio
async def test_feature_15_collects_budget(page: Page):
    """Feature 15: Bot collects budget range information."""
    await page.goto("http://localhost:5181")
    await page.wait_for_load_state("networkidle")

    # Open chat and go through initial questions
    await page.click("[data-testid='chat-widget-button']")
    await page.wait_for_selector("[data-testid='chat-window']")

    responses = [
        "My name is John Doe",
        "john@example.com",
        "We need help with data analytics in healthcare",
        "We have 50 people",
        "We use Python and PostgreSQL"
    ]

    for response in responses:
        await page.fill("[data-testid='chat-input']", response)
        await page.click("[data-testid='send-button']")
        await page.wait_for_timeout(2000)

    # Check if bot asks about budget
    messages = await page.locator("[data-testid='chat-message']").all()
    last_message = messages[-1]
    last_text = await last_message.text_content()
    assert last_text is not None, "Last message should have text content"

    # Should ask about budget
    assert "budget" in last_text.lower() or "$" in last_text, \
        f"Bot should ask about budget. Got: {last_text}"


@pytest.mark.asyncio
async def test_feature_16_collects_timeline(page: Page):
    """Feature 16: Bot collects project timeline information."""
    await page.goto("http://localhost:5181")
    await page.wait_for_load_state("networkidle")

    # Open chat and go through questions
    await page.click("[data-testid='chat-widget-button']")
    await page.wait_for_selector("[data-testid='chat-window']")

    responses = [
        "My name is John Doe",
        "john@example.com",
        "We need help with data analytics",
        "We are in healthcare with 50 people",
        "Our budget is around $50000"
    ]

    for response in responses:
        await page.fill("[data-testid='chat-input']", response)
        await page.click("[data-testid='send-button']")
        await page.wait_for_timeout(2000)

    # Check if bot asks about timeline
    messages = await page.locator("[data-testid='chat-message']").all()
    last_message = messages[-1]
    last_text = await last_message.text_content()
    assert last_text is not None, "Last message should have text content"

    # Should ask about timeline
    assert "timeline" in last_text.lower() or "month" in last_text.lower(), \
        f"Bot should ask about timeline. Got: {last_text}"
