"""E2E tests for conversation summary workflow using Playwright."""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_summary_generation_and_approval(page: Page, base_url: str):
    """Test the full summary generation and approval workflow."""
    # Navigate to the application
    page.goto(base_url)

    # Wait for chat widget to be visible
    chat_button = page.get_by_test_id("chat-widget-button")
    expect(chat_button).to_be_visible()
    chat_button.click()

    # Wait for chat window
    chat_window = page.get_by_test_id("chat-window")
    expect(chat_window).to_be_visible()

    # Send initial message
    input_field = page.get_by_test_id("message-input")
    input_field.fill("Hi, I'm John from Acme Corp")
    send_button = page.get_by_test_id("send-button")
    send_button.click()

    # Wait for response
    page.wait_for_timeout(1000)

    # Send more messages to build conversation context
    input_field.fill("We need help with our e-commerce platform")
    send_button.click()
    page.wait_for_timeout(1000)

    input_field.fill("Budget is $50k, timeline 2 months")
    send_button.click()
    page.wait_for_timeout(1000)

    # Click Generate PRD button
    prd_button = page.get_by_test_id("generate-prd-button")
    expect(prd_button).to_be_enabled()
    prd_button.click()

    # Verify summary generation indicator appears
    summary_generating = page.get_by_test_id("summary-generating")
    expect(summary_generating).to_be_visible()

    # Wait for summary review UI to appear
    page.wait_for_timeout(2000)

    # Verify we're in summary review mode
    # The summary should be displayed
    summary_content = page.locator("text=Conversation Summary")
    expect(summary_content).to_be_visible()

    # Verify approve and regenerate buttons are visible
    approve_button = page.get_by_test_id("approve-summary-button")
    regenerate_button = page.get_by_test_id("regenerate-summary-button")
    cancel_button = page.get_by_test_id("cancel-summary-button")

    expect(approve_button).to_be_visible()
    expect(regenerate_button).to_be_visible()
    expect(cancel_button).to_be_visible()

    # Click approve
    approve_button.click()

    # Verify PRD generation indicator appears
    prd_generating = page.get_by_test_id("prd-generating")
    expect(prd_generating).to_be_visible()

    # Wait for PRD to be generated
    page.wait_for_timeout(3000)

    # Verify PRD preview card appears
    prd_preview = page.get_by_test_id("prd-preview-card")
    expect(prd_preview).to_be_visible()

    # Verify download button exists
    download_button = page.get_by_test_id("download-prd-button")
    expect(download_button).to_be_visible()


@pytest.mark.e2e
def test_summary_regeneration(page: Page, base_url: str):
    """Test the summary regeneration workflow."""
    # Navigate to the application
    page.goto(base_url)

    # Open chat
    chat_button = page.get_by_test_id("chat-widget-button")
    chat_button.click()

    chat_window = page.get_by_test_id("chat-window")
    expect(chat_window).to_be_visible()

    # Build conversation
    input_field = page.get_by_test_id("message-input")
    send_button = page.get_by_test_id("send-button")

    input_field.fill("Hello, I'm Sarah from TechCorp")
    send_button.click()
    page.wait_for_timeout(800)

    input_field.fill("We need a mobile app for logistics")
    send_button.click()
    page.wait_for_timeout(800)

    # Generate PRD (which triggers summary)
    prd_button = page.get_by_test_id("generate-prd-button")
    prd_button.click()

    # Wait for summary review
    page.wait_for_timeout(2000)

    # Click regenerate instead of approve
    regenerate_button = page.get_by_test_id("regenerate-summary-button")
    regenerate_button.click()

    # Verify new summary is being generated
    summary_generating = page.get_by_test_id("summary-generating")
    expect(summary_generating).to_be_visible()

    # Wait for new summary
    page.wait_for_timeout(2000)

    # Should still be in review mode
    approve_button = page.get_by_test_id("approve-summary-button")
    expect(approve_button).to_be_visible()


@pytest.mark.e2e
def test_summary_cancellation(page: Page, base_url: str):
    """Test cancelling the summary review."""
    # Navigate to the application
    page.goto(base_url)

    # Open chat
    chat_button = page.get_by_test_id("chat-widget-button")
    chat_button.click()

    # Build conversation
    input_field = page.get_by_test_id("message-input")
    send_button = page.get_by_test_id("send-button")

    input_field.fill("Hi, I'm Mike from DataCorp")
    send_button.click()
    page.wait_for_timeout(800)

    input_field.fill("Need data analytics platform")
    send_button.click()
    page.wait_for_timeout(800)

    # Generate PRD
    prd_button = page.get_by_test_id("generate-prd-button")
    prd_button.click()

    # Wait for summary review
    page.wait_for_timeout(2000)

    # Click cancel
    cancel_button = page.get_by_test_id("cancel-summary-button")
    cancel_button.click()

    # Should be back to normal chat view
    # Verify PRD button is visible again
    prd_button = page.get_by_test_id("generate-prd-button")
    expect(prd_button).to_be_visible()


@pytest.mark.e2e
def test_summary_in_messages(page: Page, base_url: str):
    """Test that summary appears in the message history."""
    # Navigate to the application
    page.goto(base_url)

    # Open chat
    chat_button = page.get_by_test_id("chat-widget-button")
    chat_button.click()

    # Build conversation
    input_field = page.get_by_test_id("message-input")
    send_button = page.get_by_test_id("send-button")

    input_field.fill("Hi, I'm Lisa from HealthTech")
    send_button.click()
    page.wait_for_timeout(800)

    input_field.fill("Need HIPAA compliant platform")
    send_button.click()
    page.wait_for_timeout(800)

    # Generate PRD
    prd_button = page.get_by_test_id("generate-prd-button")
    prd_button.click()

    # Wait for summary review
    page.wait_for_timeout(2000)

    # Approve
    approve_button = page.get_by_test_id("approve-summary-button")
    approve_button.click()

    # Wait for PRD generation
    page.wait_for_timeout(3000)

    # Check messages container for summary-related messages
    messages_container = page.get_by_test_id("messages-container")

    # Should have messages about summary generation and approval
    expect(messages_container).to_contain_text("Summary")
    expect(messages_container).to_contain_text("approved")


@pytest.mark.e2e
def test_summary_generation_error_handling(page: Page, base_url: str):
    """Test error handling when summary generation fails."""
    # Navigate to the application
    page.goto(base_url)

    # Open chat
    chat_button = page.get_by_test_id("chat-widget-button")
    chat_button.click()

    # Try to generate PRD without enough context
    # (This should show an error or be disabled)
    prd_button = page.get_by_test_id("generate-prd-button")

    # The button should be disabled initially
    expect(prd_button).to_be_disabled()
