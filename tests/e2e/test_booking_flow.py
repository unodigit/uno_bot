"""End-to-end tests for Booking Flow functionality."""
import re

from playwright.sync_api import Page, expect

# Frontend URL
FRONTEND_URL = "http://localhost:5173"


def _accept_consent(page: Page):
    """Helper to accept GDPR consent modal if it appears."""
    try:
        consent_modal = page.locator('text=Privacy & Data Consent')
        if consent_modal.is_visible(timeout=2000):
            page.locator('.max-h-[60vh]').scroll_to_position(0, 1000)
            page.wait_for_timeout(500)
            accept_btn = page.locator('button:has-text("I Agree")')
            if accept_btn.is_visible():
                accept_btn.click()
                page.wait_for_timeout(500)
    except:
        pass


class TestBookingFlow:
    """Test cases for complete booking flow."""

    def test_complete_booking_flow(self, page: Page):
        """Test complete booking flow from expert matching to confirmation."""
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")
        page.evaluate("localStorage.clear()")
        page.context.clear_cookies()
        page.reload()
        page.wait_for_load_state("networkidle")

        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_selector('[data-testid="chat-window"]', state="visible")
        _accept_consent(page)

        chat_input = page.get_by_test_id("message-input")
        send_button = page.get_by_test_id("send-button")

        chat_input.fill("John Doe")
        send_button.click()
        page.wait_for_timeout(1500)

        chat_input.fill("john.doe@example.com")
        send_button.click()
        page.wait_for_timeout(1500)

        chat_input.fill("We need help with AI strategy and machine learning implementation")
        send_button.click()
        page.wait_for_timeout(2000)

        match_experts_btn = page.get_by_test_id("match-experts-button")
        expect(match_experts_btn).to_be_visible(timeout=10000)
        match_experts_btn.click()

        expect(page.get_by_test_id("expert-match-list")).to_be_visible(timeout=10000)
        page.wait_for_timeout(1000)

        book_expert_btn = page.get_by_test_id("book-expert-0")
        expect(book_expert_btn).to_be_visible(timeout=5000)
        book_expert_btn.click()

        page.wait_for_selector('text=Select Time Slot', timeout=10000)

        slot_buttons = page.locator('button').filter(has_text=re.compile(r'\d{1,2}:\d{2}'))
        expect(slot_buttons.first).to_be_visible(timeout=5000)
        slot_buttons.first.click()

        confirm_btn = page.locator('button:has-text("Confirm Booking")')
        expect(confirm_btn).to_be_visible(timeout=5000)

        name_input = page.locator('input[placeholder*="name" i], input[name*="name" i]').first
        email_input = page.locator('input[placeholder*="email" i], input[name*="email" i]').first

        if name_input.is_visible():
            name_input.fill("John Doe")
        if email_input.is_visible():
            email_input.fill("john.doe@example.com")

        confirm_btn.click()
        page.wait_for_timeout(3000)

        expect(page.locator('text=Booking Confirmed')).to_be_visible(timeout=10000)
        expect(page.locator('text=Meeting Link')).to_be_visible(timeout=5000)

        print("✓ Complete booking flow test passed")

    def test_time_slot_selection_confirmation(self, page: Page):
        """Test: Time slot selection shows confirmation UI."""
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")
        page.evaluate("localStorage.clear()")
        page.context.clear_cookies()
        page.reload()
        page.wait_for_load_state("networkidle")

        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_selector('[data-testid="chat-window"]', state="visible")
        _accept_consent(page)

        chat_input = page.get_by_test_id("message-input")
        send_button = page.get_by_test_id("send-button")

        chat_input.fill("Test User")
        send_button.click()
        page.wait_for_timeout(800)

        chat_input.fill("test@example.com")
        send_button.click()
        page.wait_for_timeout(800)

        chat_input.fill("Need AI help")
        send_button.click()
        page.wait_for_timeout(2000)

        match_experts_btn = page.get_by_test_id("match-experts-button")
        expect(match_experts_btn).to_be_visible(timeout=10000)
        match_experts_btn.click()
        expect(page.get_by_test_id("expert-match-list")).to_be_visible(timeout=10000)
        page.wait_for_timeout(1000)

        book_expert_btn = page.get_by_test_id("book-expert-0")
        expect(book_expert_btn).to_be_visible(timeout=5000)
        book_expert_btn.click()

        page.wait_for_selector('text=Select Time Slot', timeout=10000)

        slot_buttons = page.locator('button').filter(has_text=re.compile(r'\d{1,2}:\d{2}'))
        expect(slot_buttons.first).to_be_visible(timeout=5000)
        slot_buttons.first.click()

        expect(page.locator('text=Selected:')).to_be_visible(timeout=5000)
        expect(page.locator('button:has-text("Confirm Booking")')).to_be_visible(timeout=5000)

        print("✓ Time slot selection confirmation test passed")
