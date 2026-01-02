"""End-to-end tests for PRD generation functionality."""
import pytest
from playwright.sync_api import Page, expect


def test_prd_preview_displays_in_chat_interface(page: Page):
    """Test that PRD preview displays correctly in chat interface."""
    page.goto("http://localhost:5173")

    # Open chat widget
    page.click('[data-testid="chat-widget-button"]')
    page.wait_for_selector('[data-testid="chat-window"]', state="visible")

    # Complete qualification conversation to reach PRD phase
    chat_input = page.locator('[data-testid="message-input"]')
    send_button = page.locator('[data-testid="send-button"]')

    # Send name
    chat_input.fill("My name is Test User")
    send_button.click()
    page.wait_for_timeout(1000)

    # Send email
    chat_input.fill("test@example.com")
    send_button.click()
    page.wait_for_timeout(1000)

    # Send business context
    chat_input.fill("We need help with AI and data analytics")
    send_button.click()
    page.wait_for_timeout(1000)

    # Send company info
    chat_input.fill("I work at TechCorp")
    send_button.click()
    page.wait_for_timeout(1000)

    # Send budget and timeline
    chat_input.fill("Budget is $75,000")
    send_button.click()
    page.wait_for_timeout(1000)

    chat_input.fill("Timeline is 3 months")
    send_button.click()
    page.wait_for_timeout(2000)

    # Generate PRD
    chat_input.fill("Generate PRD")
    send_button.click()
    page.wait_for_timeout(3000)

    # Verify PRD preview appears
    prd_preview = page.locator('[data-testid="prd-preview-card"]')
    expect(prd_preview).to_be_visible()

    # Verify PRD preview content
    expect(prd_preview.locator('text=PRD Generated!')).to_be_visible()
    expect(prd_preview.locator('[data-testid="download-prd-button"]')).to_be_visible()

    # Verify filename is displayed
    expect(prd_preview.locator('text=PRD_')).to_be_visible()


def test_prd_download_functionality(page: Page):
    """Test that PRD download works correctly."""
    page.goto("http://localhost:5173")
    page.click('[data-testid="chat-widget-button"]')
    page.wait_for_selector('[data-testid="chat-window"]')

    # Complete conversation and generate PRD (same as above)
    chat_input = page.locator('[data-testid="message-input"]')
    send_button = page.locator('[data-testid="send-button"]')

    messages = [
        "My name is Test User",
        "test@example.com",
        "We need help with AI and data analytics",
        "I work at TechCorp",
        "Budget is $75,000",
        "Timeline is 3 months",
        "Generate PRD"
    ]

    for msg in messages:
        chat_input.fill(msg)
        send_button.click()
        page.wait_for_timeout(1500)

    # Wait for PRD preview to appear
    prd_preview = page.locator('[data-testid="prd-preview-card"]')
    expect(prd_preview).to_be_visible()

    # Click download button
    download_button = page.locator('[data-testid="download-prd-button"]')
    expect(download_button).to_be_visible()

    # Verify download button is clickable and has correct text
    expect(download_button).to_contain_text("Download")
    expect(download_button.locator('svg')).to_be_visible()  # Download icon

    # Test that clicking download doesn't cause errors
    page.evaluate('''() => {
        const button = document.querySelector('[data-testid="download-prd-button"]');
        if (button) {
            button.click();
        }
    }''')

    # Should not show any error messages
    error_banner = page.locator('.bg-error')
    expect(error_banner).not_to_be_visible()


def test_prd_generation_indicator(page: Page):
    """Test that PRD generation shows loading indicator."""
    page.goto("http://localhost:5173")
    page.click('[data-testid="chat-widget-button"]')
    page.wait_for_selector('[data-testid="chat-window"]')

    # Complete qualification conversation
    chat_input = page.locator('[data-testid="message-input"]')
    send_button = page.locator('[data-testid="send-button"]')

    messages = [
        "My name is Test User",
        "test@example.com",
        "We need help with AI and data analytics",
        "I work at TechCorp",
        "Budget is $75,000",
        "Timeline is 3 months"
    ]

    for msg in messages:
        # Wait for input field to be enabled before typing
        expect(chat_input).to_be_enabled()
        chat_input.fill(msg)
        send_button.click()
        # Wait for bot response to complete
        page.wait_for_timeout(2000)

    # Generate PRD
    chat_input.fill("Generate PRD")
    send_button.click()

    # Verify loading indicator appears during generation
    loading_indicator = page.locator('[data-testid="prd-generating"]')
    expect(loading_indicator).to_be_visible()
    expect(loading_indicator.locator('text=Generating PRD...')).to_be_visible()

    # Wait for generation to complete
    page.wait_for_timeout(3000)

    # Loading indicator should disappear
    expect(loading_indicator).not_to_be_visible()

    # PRD preview should appear
    prd_preview = page.locator('[data-testid="prd-preview-card"]')
    expect(prd_preview).to_be_visible()


def test_prd_quick_reply_button(page: Page):
    """Test that PRD quick reply button works."""
    page.goto("http://localhost:5173")
    page.click('[data-testid="chat-widget-button"]')
    page.wait_for_selector('[data-testid="chat-window"]')

    # Complete qualification conversation
    chat_input = page.locator('[data-testid="message-input"]')
    send_button = page.locator('[data-testid="send-button"]')

    messages = [
        "My name is Test User",
        "test@example.com",
        "We need help with AI and data analytics",
        "I work at TechCorp",
        "Budget is $75,000",
        "Timeline is 3 months"
    ]

    for msg in messages:
        # Wait for input field to be enabled before typing
        expect(chat_input).to_be_enabled()
        chat_input.fill(msg)
        send_button.click()
        # Wait for bot response to complete
        page.wait_for_timeout(2000)

    # Look for PRD generation quick reply button
    prd_quick_reply = page.locator('button:has-text("Generate PRD")')
    expect(prd_quick_reply).to_be_visible()

    # Click quick reply
    prd_quick_reply.click()
    page.wait_for_timeout(2000)

    # Verify PRD was generated
    prd_preview = page.locator('[data-testid="prd-preview-card"]')
    expect(prd_preview).to_be_visible()
    expect(prd_preview.locator('text=PRD Generated!')).to_be_visible()


def test_prd_message_display(page: Page):
    """Test that PRD generation is communicated to user via chat messages."""
    page.goto("http://localhost:5173")
    page.click('[data-testid="chat-widget-button"]')
    page.wait_for_selector('[data-testid="chat-window"]')

    # Complete conversation and generate PRD
    chat_input = page.locator('[data-testid="message-input"]')
    send_button = page.locator('[data-testid="send-button"]')

    messages = [
        "My name is Test User",
        "test@example.com",
        "We need help with AI and data analytics",
        "I work at TechCorp",
        "Budget is $75,000",
        "Timeline is 3 months",
        "Generate PRD"
    ]

    for msg in messages:
        # Wait for input field to be enabled before typing
        expect(chat_input).to_be_enabled()
        chat_input.fill(msg)
        send_button.click()
        page.wait_for_timeout(2000)

    # Wait for PRD generation to complete - longer wait for API calls
    page.wait_for_timeout(5000)

    # Verify PRD preview appears (main indicator of successful PRD generation)
    prd_preview = page.locator('[data-testid="prd-preview-card"]')
    expect(prd_preview).to_be_visible()

    # Verify the preview shows PRD was generated
    expect(prd_preview.locator('text=PRD Generated!')).to_be_visible()