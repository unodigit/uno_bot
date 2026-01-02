"""End-to-end tests for GDPR consent functionality."""
import pytest
from playwright.sync_api import Page, expect
import re


class TestGDPRConsent:
    """Test GDPR consent collection and handling."""

    def test_consent_modal_appears_on_chat_open(self, page: Page):
        """
        Test: Consent modal appears when chat opens and no consent given

        Steps:
        1. Navigate to main page
        2. Open chat widget
        3. Verify consent modal appears
        4. Verify modal contains privacy information
        """
        # Navigate to main page
        page.goto("http://localhost:5173")
        page.wait_for_load_state("networkidle")

        # Clear any existing consent
        page.evaluate("localStorage.removeItem('uno_consent')")

        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_selector('[data-testid="chat-window"]', state="visible")

        # Verify consent modal appears
        consent_modal = page.locator('[data-testid="consent-modal"]')
        expect(consent_modal).to_be_visible(timeout=5000)

        # Verify modal content
        expect(page.locator('text=Privacy & Data Consent')).to_be_visible()
        expect(page.locator('text=Data Collection & Processing')).to_be_visible()
        expect(page.locator('text=personal information, business context')).to_be_visible()

        print("✓ Consent modal appears on chat open")

    def test_consent_accept_functionality(self, page: Page):
        """
        Test: User can accept consent and proceed

        Steps:
        1. Open chat and show consent modal
        2. Accept consent
        3. Verify modal closes
        4. Verify consent stored in localStorage
        5. Verify chat continues normally
        """
        # Navigate and clear consent
        page.goto("http://localhost:5173")
        page.wait_for_load_state("networkidle")
        page.evaluate("localStorage.removeItem('uno_consent')")

        # Open chat
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_selector('[data-testid="chat-window"]', state="visible")

        # Accept consent
        accept_button = page.locator('button:has-text("I Agree - Continue")')
        expect(accept_button).to_be_visible(timeout=5000)
        accept_button.click()

        # Verify modal closes
        expect(page.locator('[data-testid="consent-modal"]')).not_to_be_visible()

        # Verify consent stored in localStorage
        consent_data = page.evaluate("localStorage.getItem('uno_consent')")
        assert consent_data is not None
        import json
        consent_obj = json.loads(consent_data)
        assert consent_obj["accepted"] is True
        assert consent_obj["version"] == "1.0"

        # Verify chat continues
        expect(page.get_by_test_id("message-input")).to_be_visible()
        expect(page.get_by_test_id("send-button")).to_be_visible()

        print("✓ Consent acceptance works correctly")

    def test_consent_decline_functionality(self, page: Page):
        """
        Test: User can decline consent and chat is limited

        Steps:
        1. Open chat and show consent modal
        2. Decline consent
        3. Verify modal closes
        4. Verify consent stored as declined
        5. Verify chat shows limited functionality
        """
        # Navigate and clear consent
        page.goto("http://localhost:5173")
        page.wait_for_load_state("networkidle")
        page.evaluate("localStorage.removeItem('uno_consent')")

        # Open chat
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_selector('[data-testid="chat-window"]', state="visible")

        # Decline consent
        decline_button = page.locator('button:has-text("Decline")')
        expect(decline_button).to_be_visible(timeout=5000)
        decline_button.click()

        # Verify modal closes
        expect(page.locator('[data-testid="consent-modal"]')).not_to_be_visible()

        # Verify consent stored as declined
        consent_data = page.evaluate("localStorage.getItem('uno_consent')")
        assert consent_data is not None
        import json
        consent_obj = json.loads(consent_data)
        assert consent_obj["accepted"] is False
        assert consent_obj["declined"] is True

        # Verify chat shows limited functionality message
        expect(page.locator('text=not be able to use our consultation services')).to_be_visible()

        print("✓ Consent decline works correctly")

    def test_consent_respects_scroll_requirement(self, page: Page):
        """
        Test: Accept button is disabled until user scrolls

        Steps:
        1. Open chat and show consent modal
        2. Verify Accept button is initially disabled
        3. Scroll through content
        4. Verify Accept button becomes enabled
        """
        # Navigate and clear consent
        page.goto("http://localhost:5173")
        page.wait_for_load_state("networkidle")
        page.evaluate("localStorage.removeItem('uno_consent')")

        # Open chat
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_selector('[data-testid="chat-window"]', state="visible")

        # Verify Accept button is initially disabled
        accept_button = page.locator('button:has-text("I Agree - Continue")')
        expect(accept_button).to_be_visible(timeout=5000)
        expect(accept_button).to_be_disabled()

        # Scroll through content
        page.locator('.consent-content').evaluate('(element) => { element.scrollTop = 1000; }')

        # Verify Accept button becomes enabled after scrolling
        expect(accept_button).not_to_be_disabled()

        print("✓ Scroll requirement for consent acceptance works")

    def test_consent_not_shown_when_already_given(self, page: Page):
        """
        Test: Consent modal doesn't show if already given

        Steps:
        1. Set existing consent in localStorage
        2. Open chat
        3. Verify consent modal doesn't appear
        4. Verify chat proceeds normally
        """
        # Set existing consent
        import json
        consent_data = json.dumps({
            "accepted": True,
            "timestamp": "2024-01-01T12:00:00Z",
            "version": "1.0"
        })
        page.goto("http://localhost:5173")
        page.wait_for_load_state("networkidle")
        page.evaluate(f"localStorage.setItem('uno_consent', {json.dumps(consent_data)})")

        # Open chat
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_selector('[data-testid="chat-window"]', state="visible")

        # Verify consent modal doesn't appear
        expect(page.locator('[data-testid="consent-modal"]')).not_to_be_visible()

        # Verify chat proceeds normally
        expect(page.get_by_test_id("message-input")).to_be_visible()
        expect(page.get_by_test_id("send-button")).to_be_visible()

        print("✓ Existing consent is respected")

    def test_consent_modal_content_compliance(self, page: Page):
        """
        Test: Consent modal contains required GDPR information

        Steps:
        1. Open chat and show consent modal
        2. Verify all required sections are present
        3. Verify data types are listed
        4. Verify rights are explained
        """
        # Navigate and clear consent
        page.goto("http://localhost:5173")
        page.wait_for_load_state("networkidle")
        page.evaluate("localStorage.removeItem('uno_consent')")

        # Open chat
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_selector('[data-testid="chat-window"]', state="visible")

        # Verify required sections are present
        expect(page.locator('text=Data Collection & Processing')).to_be_visible()
        expect(page.locator('text=How we use your data')).to_be_visible()
        expect(page.locator('text=Your rights')).to_be_visible()
        expect(page.locator('text=UnoDigit Business Consultation')).to_be_visible()

        # Verify data types are listed
        expect(page.locator('text=Personal Information: Name, email address')).to_be_visible()
        expect(page.locator('text=Business Context: Industry, company size')).to_be_visible()
        expect(page.locator('text=Conversation Data: Chat messages')).to_be_visible()
        expect(page.locator('text=Technical Data: Browser information')).to_be_visible()

        # Verify rights are explained
        expect(page.locator('text=Right to access, correct, or delete')).to_be_visible()
        expect(page.locator('text=Right to withdraw consent')).to_be_visible()
        expect(page.locator('text=Right to data portability')).to_be_visible()

        print("✓ Consent modal contains all required GDPR information")