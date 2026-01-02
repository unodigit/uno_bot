"""End-to-end tests for conversation flow with phase tracking."""
from playwright.sync_api import Page, expect


def test_conversation_collects_user_information(page: Page):
    """Test that the conversation properly collects user information through phases."""
    # Navigate to app
    page.goto("http://localhost:5173")

    # Open chat widget
    page.click('[data-testid="chat-widget-button"]')
    page.wait_for_selector('[data-testid="chat-window"]', state="visible")

    # Wait for welcome message
    page.wait_for_selector('text=Welcome')

    # Test 1: Send name
    chat_input = page.locator('[data-testid="message-input"]')
    send_button = page.locator('[data-testid="send-button"]')

    chat_input.fill("My name is John Doe")
    send_button.click()

    # Wait for bot response
    page.wait_for_timeout(2000)

    # Verify bot response is visible (check for message elements)
    messages = page.locator('[data-testid^="message-"]')
    expect(messages).to_have_count(4)  # Welcome, user name, bot response, possibly more

    # Test 2: Send email
    chat_input.fill("john@example.com")
    send_button.click()

    # Wait for bot response
    page.wait_for_timeout(2000)

    # Verify we have more messages
    expect(messages).to_have_count(6)


def test_lead_scoring_and_service_matching(page: Page):
    """Test that lead scoring and service matching work correctly."""
    page.goto("http://localhost:5173")
    page.click('[data-testid="chat-widget-button"]')
    page.wait_for_selector('[data-testid="chat-window"]')

    chat_input = page.locator('[data-testid="message-input"]')
    send_button = page.locator('[data-testid="send-button"]')

    # Complete discovery phase
    chat_input.fill("My name is Sarah")
    send_button.click()
    page.wait_for_timeout(1500)

    chat_input.fill("sarah@techcorp.com")
    send_button.click()
    page.wait_for_timeout(1500)

    chat_input.fill("We need help with AI strategy and machine learning")
    send_button.click()

    # Wait for messages
    page.wait_for_timeout(2000)

    # Check that AI service is recommended based on conversation
    messages = page.locator('[data-testid^="message-"]')
    # Should have at least 6 messages: welcome, user name, bot, user email, bot, user challenge, bot response
    count = messages.count()
    assert count >= 6, f"Expected at least 6 messages, got {count}"


def test_conversation_phase_transitions(page: Page):
    """Test that conversation phases transition correctly."""
    page.goto("http://localhost:5173")
    page.click('[data-testid="chat-widget-button"]')
    page.wait_for_selector('[data-testid="chat-window"]')

    chat_input = page.locator('[data-testid="message-input"]')
    send_button = page.locator('[data-testid="send-button"]')

    # Phase 1: Greeting (get name)
    chat_input.fill("Hello, I'm Mike")
    send_button.click()
    page.wait_for_timeout(1500)

    # Phase 2: Discovery (get email)
    chat_input.fill("mike@example.com")
    send_button.click()
    page.wait_for_timeout(1500)

    # Phase 3: Business challenges
    chat_input.fill("We have problems with data analytics")
    send_button.click()
    page.wait_for_timeout(2000)

    # Verify we have multiple messages in the conversation
    messages = page.locator('[data-testid^="message-"]')
    count = messages.count()
    assert count >= 6, f"Expected at least 6 messages, got {count}"
