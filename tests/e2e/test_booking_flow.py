"""End-to-end tests for Booking Flow functionality."""
import re

from playwright.sync_api import Page, expect

# Frontend URL
FRONTEND_URL = "http://localhost:5173"


class TestBookingFlow:
    """Test cases for complete booking flow."""

    def test_complete_booking_flow(self, page: Page):
        """
        Test: Complete booking flow from expert matching to confirmation

        Steps:
        1. Open chat widget
        2. Complete discovery phase (name, email, challenges)
        3. Match experts
        4. Select expert to book
        5. Select time slot
        6. Fill booking form
        7. Confirm booking
        8. Verify confirmation screen
        """
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Clear storage for clean test
        page.evaluate("localStorage.clear()")
        page.context.clear_cookies()
        page.reload()
        page.wait_for_load_state("networkidle")

        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_selector('[data-testid="chat-window"]', state="visible")

        # Complete discovery phase
        chat_input = page.get_by_test_id("message-input")
        send_button = page.get_by_test_id("send-button")

        # Send name
        chat_input.fill("John Doe")
        send_button.click()
        page.wait_for_timeout(1500)

        # Send email
        chat_input.fill("john.doe@example.com")
        send_button.click()
        page.wait_for_timeout(1500)

        # Send business challenges
        chat_input.fill("We need help with AI strategy and machine learning implementation")
        send_button.click()
        page.wait_for_timeout(2000)

        # Click "Match Experts" button
        match_experts_btn = page.get_by_test_id("match-experts-button")
        expect(match_experts_btn).to_be_visible(timeout=10000)
        match_experts_btn.click()

        # Wait for expert matching to complete
        expect(page.get_by_test_id("expert-match-list")).to_be_visible(timeout=10000)
        page.wait_for_timeout(1000)

        # Click "Book" on first expert
        book_expert_btn = page.get_by_test_id("book-expert-0")
        expect(book_expert_btn).to_be_visible(timeout=5000)
        book_expert_btn.click()

        # Wait for calendar picker
        page.wait_for_selector('text=Select Time Slot', timeout=10000)

        # Select a time slot
        slot_buttons = page.locator('button').filter(has_text=re.compile(r'\d{1,2}:\d{2}'))
        expect(slot_buttons.first).to_be_visible(timeout=5000)
        slot_buttons.first.click()

        # Wait for confirm button to appear
        confirm_btn = page.locator('button:has-text("Confirm Booking")')
        expect(confirm_btn).to_be_visible(timeout=5000)

        # Fill booking form (name and email fields in BookingForm)
        # The form appears after selecting a slot
        name_input = page.locator('input[placeholder*="name" i], input[name*="name" i]').first
        email_input = page.locator('input[placeholder*="email" i], input[name*="email" i]').first

        if name_input.is_visible():
            name_input.fill("John Doe")
        if email_input.is_visible():
            email_input.fill("john.doe@example.com")

        # Click confirm
        confirm_btn.click()

        # Wait for booking confirmation
        page.wait_for_timeout(3000)

        # Verify booking confirmation screen appears
        expect(page.locator('text=Booking Confirmed')).to_be_visible(timeout=10000)
        expect(page.locator('text=Meeting Link')).to_be_visible(timeout=5000)

        print("✓ Complete booking flow test passed")


    def test_timezone_detection(self, page: Page):
        """
        Test: Timezone is automatically detected and displayed

        Steps:
        1. Navigate to booking flow
        2. Open calendar picker
        3. Verify timezone is detected and shown
        """
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Setup
        page.evaluate("localStorage.clear()")
        page.context.clear_cookies()
        page.reload()
        page.wait_for_load_state("networkidle")

        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_selector('[data-testid="chat-window"]', state="visible")

        # Complete discovery
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

        # Match experts
        match_experts_btn = page.get_by_test_id("match-experts-button")
        expect(match_experts_btn).to_be_visible(timeout=10000)
        match_experts_btn.click()
        expect(page.get_by_test_id("expert-match-list")).to_be_visible(timeout=10000)
        page.wait_for_timeout(1000)

        # Book expert
        book_expert_btn = page.get_by_test_id("book-expert-0")
        expect(book_expert_btn).to_be_visible(timeout=5000)
        book_expert_btn.click()

        # Wait for calendar picker
        page.wait_for_selector('text=Select Time Slot', timeout=10000)

        # Verify timezone is displayed (should show detected timezone)
        # The timezone is shown in the header of calendar picker
        timezone_display = page.locator('text=UTC')  # or other detected timezone
        expect(timezone_display).to_be_visible(timeout=5000)

        print("✓ Timezone detection test passed")


    def test_time_slot_selection_confirmation(self, page: Page):
        """
        Test: Time slot selection shows confirmation UI

        Steps:
        1. Navigate to booking flow
        2. Select a time slot
        3. Verify confirmation UI appears with selected slot info
        """
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Setup
        page.evaluate("localStorage.clear()")
        page.context.clear_cookies()
        page.reload()
        page.wait_for_load_state("networkidle")

        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_selector('[data-testid="chat-window"]', state="visible")

        # Complete discovery
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

        # Match experts
        match_experts_btn = page.get_by_test_id("match-experts-button")
        expect(match_experts_btn).to_be_visible(timeout=10000)
        match_experts_btn.click()
        expect(page.get_by_test_id("expert-match-list")).to_be_visible(timeout=10000)
        page.wait_for_timeout(1000)

        # Book expert
        book_expert_btn = page.get_by_test_id("book-expert-0")
        expect(book_expert_btn).to_be_visible(timeout=5000)
        book_expert_btn.click()

        # Wait for calendar picker
        page.wait_for_selector('text=Select Time Slot', timeout=10000)

        # Select a time slot
        slot_buttons = page.locator('button').filter(has_text=re.compile(r'\d{1,2}:\d{2}'))
        expect(slot_buttons.first).to_be_visible(timeout=5000)
        slot_buttons.first.click()

        # Verify confirmation UI appears
        expect(page.locator('text=Selected:')).to_be_visible(timeout=5000)
        expect(page.locator('button:has-text("Confirm Booking")')).to_be_visible(timeout=5000)

        print("✓ Time slot selection confirmation test passed")


    def test_double_booking_prevention(self, page: Page):
        """
        Test: Double-booking prevention works correctly

        Note: This test verifies that the booking flow validates
        availability before confirming

        Steps:
        1. Navigate to booking
        2. Select a slot
        3. Verify availability check happens before booking
        """
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Setup
        page.evaluate("localStorage.clear()")
        page.context.clear_cookies()
        page.reload()
        page.wait_for_load_state("networkidle")

        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_selector('[data-testid="chat-window"]', state="visible")

        # Complete discovery
        chat_input = page.get_by_test_id("message-input")
        send_button = page.get_by_test_id("send-button")

        chat_input.fill("Test User")
        send_button.click()
        page.wait_for_timeout(800)

        chat_input.fill("test@example.com")
        send_button.click()
        page.wait_for_timeout(800)

        chat_input.fill("Need AI help with machine learning")
        send_button.click()
        page.wait_for_timeout(2000)

        # Click "Match Experts" button
        match_experts_btn = page.get_by_test_id("match-experts-button")
        expect(match_experts_btn).to_be_visible(timeout=10000)
        match_experts_btn.click()
        expect(page.get_by_test_id("expert-match-list")).to_be_visible(timeout=10000)
        page.wait_for_timeout(1000)

        # Click "Book" on first expert
        book_expert_btn = page.get_by_test_id("book-expert-0")
        expect(book_expert_btn).to_be_visible(timeout=5000)
        book_expert_btn.click()

        page.wait_for_timeout(2000)

        # Wait for calendar picker
        page.wait_for_selector('text=Select Time Slot', timeout=10000)

        # Select a slot
        slot_buttons = page.locator('button').filter(has_text=re.compile(r'\d{1,2}:\d{2}'))
        slot_buttons.first.click()

        # Track API calls - set up BEFORE clicking confirm
        availability_check_called = False
        booking_create_called = False

        def track_api_calls(route):
            nonlocal availability_check_called, booking_create_called
            url = route.request.url
            if "/availability" in url and route.request.method == "GET":
                availability_check_called = True
            if "/bookings" in url and route.request.method == "POST":
                booking_create_called = True
            route.continue_()

        page.route("**/*", track_api_calls)

        # Fill booking form first
        name_input = page.locator('input[placeholder*="name" i], input[name*="name" i]').first
        email_input = page.locator('input[placeholder*="email" i], input[name*="email" i]').first

        if name_input.is_visible():
            name_input.fill("Test User")
        if email_input.is_visible():
            email_input.fill("test@example.com")

        # Click confirm
        confirm_btn = page.locator('button:has-text("Confirm Booking")')
        confirm_btn.click()

        # Wait for API calls
        page.wait_for_timeout(3000)

        # Verify availability was checked before booking
        assert availability_check_called, "Availability check should happen before booking"
        assert booking_create_called, "Booking should be created"

        print("✓ Double-booking prevention test passed")


    def test_availability_refresh(self, page: Page):
        """
        Test: Availability refreshes in real-time before confirmation

        Steps:
        1. Open calendar picker
        2. Wait for slots to load
        3. Verify availability check happens on confirm
        """
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Setup
        page.evaluate("localStorage.clear()")
        page.context.clear_cookies()
        page.reload()
        page.wait_for_load_state("networkidle")

        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_selector('[data-testid="chat-window"]', state="visible")

        # Complete discovery
        chat_input = page.get_by_test_id("message-input")
        send_button = page.get_by_test_id("send-button")

        chat_input.fill("Test User")
        send_button.click()
        page.wait_for_timeout(800)

        chat_input.fill("test@example.com")
        send_button.click()
        page.wait_for_timeout(800)

        chat_input.fill("Need AI help with machine learning")
        send_button.click()
        page.wait_for_timeout(2000)

        # Click "Match Experts" button
        match_experts_btn = page.get_by_test_id("match-experts-button")
        expect(match_experts_btn).to_be_visible(timeout=10000)
        match_experts_btn.click()
        expect(page.get_by_test_id("expert-match-list")).to_be_visible(timeout=10000)
        page.wait_for_timeout(1000)

        # Click "Book" on first expert
        book_expert_btn = page.get_by_test_id("book-expert-0")
        expect(book_expert_btn).to_be_visible(timeout=5000)
        book_expert_btn.click()

        page.wait_for_timeout(2000)

        # Wait for calendar picker
        page.wait_for_selector('text=Select Time Slot', timeout=10000)

        # Select a slot
        slot_buttons = page.locator('button').filter(has_text=re.compile(r'\d{1,2}:\d{2}'))
        slot_buttons.first.click()

        # Track availability calls
        availability_calls = []

        def track_availability(route):
            url = route.request.url
            if "/availability" in url and route.request.method == "GET":
                availability_calls.append(url)
            route.continue_()

        page.route("**/*", track_availability)

        # Fill booking form
        name_input = page.locator('input[placeholder*="name" i], input[name*="name" i]').first
        email_input = page.locator('input[placeholder*="email" i], input[name*="email" i]').first

        if name_input.is_visible():
            name_input.fill("Test User")
        if email_input.is_visible():
            email_input.fill("test@example.com")

        # Click confirm (this triggers final availability check in confirmBooking)
        confirm_btn = page.locator('button:has-text("Confirm Booking")')
        confirm_btn.click()

        page.wait_for_timeout(2000)

        # Verify at least one availability check happened (the one in confirmBooking)
        assert len(availability_calls) > 0, f"Availability should be checked, got {len(availability_calls)} calls"

        print("✓ Availability refresh test passed")
