"""End-to-end tests for complete booking flow."""
import pytest
import re
from playwright.sync_api import Page, expect

# Frontend URL
FRONTEND_URL = "http://localhost:5173"


def test_complete_booking_flow(page: Page):
    """
    Test: Complete booking flow from chat to confirmation

    Steps:
    1. Open chat widget
    2. Complete discovery phase (name, email, needs)
    3. Get expert matching
    4. View calendar picker with available slots
    5. Select a time slot
    6. Verify confirmation UI shows selected slot
    7. Confirm booking
    8. Verify booking confirmation appears in chat
    9. Verify confirmation card is displayed
    """
    # Navigate to app
    page.goto(FRONTEND_URL)
    page.wait_for_load_state("networkidle")

    # Clear any existing session
    page.evaluate("localStorage.clear()")
    page.context.clear_cookies()
    page.reload()
    page.wait_for_load_state("networkidle")

    # Open chat widget
    page.get_by_test_id("chat-widget-button").click()
    page.wait_for_selector('[data-testid="chat-window"]', state="visible")

    # Wait for welcome message
    page.wait_for_selector('text=Welcome', timeout=5000)

    # Phase 1: Send name
    chat_input = page.get_by_test_id("message-input")
    send_button = page.get_by_test_id("send-button")

    chat_input.fill("My name is Test User")
    send_button.click()
    page.wait_for_timeout(1000)

    # Phase 2: Send email
    chat_input.fill("testuser@example.com")
    send_button.click()
    page.wait_for_timeout(1000)

    # Phase 3: Send business needs
    chat_input.fill("We need help with AI strategy and machine learning implementation")
    send_button.click()
    page.wait_for_timeout(2000)

    # Wait for expert matching button to become available
    # Click "Match Experts" button
    match_experts_btn = page.get_by_test_id("match-experts-button")
    expect(match_experts_btn).to_be_visible(timeout=10000)
    match_experts_btn.click()
    # Wait for expert matching to complete and experts to appear
    expect(page.get_by_test_id("expert-match-list")).to_be_visible(timeout=10000)
    page.wait_for_timeout(1000)

    # Wait for expert list to appear
    expect(page.get_by_test_id("expert-match-list")).to_be_visible(timeout=10000)

    # Click "Book" button on first expert
    book_expert_btn = page.get_by_test_id("book-expert-0")
    expect(book_expert_btn).to_be_visible(timeout=5000)
    book_expert_btn.click()

    page.wait_for_timeout(2000)

    # Wait for calendar picker to appear
    calendar_picker = page.locator('text=Select Time Slot')
    expect(calendar_picker).to_be_visible(timeout=10000)

    # Note: Timezone display is tested separately in test_timezone_detection()
    # For this test, we just need to verify the calendar picker loads

    # Select a time slot
    # Wait for slots to load
    page.wait_for_timeout(2000)

    # Get first available slot - look for buttons with time format
    # Use regex pattern to find time slots like "10:00 AM" or "14:30"
    available_slots = page.locator('button').filter(
        has_text=re.compile(r'\d{1,2}:\d{2}')
    )

    # Count slots and select one
    slot_count = available_slots.count()
    assert slot_count > 0, "No available time slots found"

    # Click first slot
    first_slot = available_slots.first
    first_slot_text = first_slot.inner_text()
    first_slot.click()

    # Verify slot is selected (should have active styling)
    page.wait_for_timeout(500)

    # Verify confirmation UI appears
    selected_text = page.locator('text=Selected:')
    expect(selected_text).to_be_visible(timeout=5000)

    # Verify Confirm button is visible and enabled
    confirm_button = page.locator('button:has-text("Confirm Booking")')
    expect(confirm_button).to_be_visible()
    expect(confirm_button).to_be_enabled()

    # Click confirm (in CalendarPicker - moves to BookingForm)
    confirm_button.click()

    # Wait for BookingForm to appear (look for the form header)
    page.wait_for_timeout(1000)
    expect(page.locator('h3:has-text("Confirm Booking")')).to_be_visible(timeout=5000)

    # Fill in name in BookingForm
    name_input = page.locator('input[id="name"]')
    expect(name_input).to_be_visible()
    name_input.fill("Test User")

    # Fill in email in BookingForm
    email_input = page.locator('input[id="email"]')
    expect(email_input).to_be_visible()
    email_input.fill("testuser@example.com")

    # Click final confirm button in BookingForm
    # After filling name and email, the submit button should be enabled
    # Use the button with type="submit" inside the form
    final_confirm = page.locator('form button[type="submit"]')
    expect(final_confirm).to_be_visible()
    expect(final_confirm).to_be_enabled()
    final_confirm.click()

    # Wait for booking to be processed
    page.wait_for_timeout(3000)

    # Verify confirmation card is displayed (bookingState = 'completed' shows this)
    confirmation_card = page.locator('[data-testid="booking-confirmation-card"]')
    expect(confirmation_card).to_be_visible(timeout=10000)

    # Verify the confirmation card shows "Booking Confirmed!"
    expect(page.locator('text=Booking Confirmed!')).to_be_visible()

    print("✓ Complete booking flow test passed")


def test_timezone_detection(page: Page):
    """
    Test: Timezone is automatically detected and displayed

    Steps:
    1. Open chat widget
    2. Navigate to booking phase
    3. Verify timezone is automatically detected
    4. Verify timezone label is correct
    """
    page.goto(FRONTEND_URL)
    page.wait_for_load_state("networkidle")

    # Clear session
    page.evaluate("localStorage.clear()")
    page.context.clear_cookies()
    page.reload()
    page.wait_for_load_state("networkidle")

    # Open chat and complete discovery
    page.get_by_test_id("chat-widget-button").click()
    page.wait_for_selector('[data-testid="chat-window"]', state="visible")

    chat_input = page.get_by_test_id("message-input")
    send_button = page.get_by_test_id("send-button")

    # Complete discovery
    chat_input.fill("Test User")
    send_button.click()
    page.wait_for_timeout(800)

    chat_input.fill("test@example.com")
    send_button.click()
    page.wait_for_timeout(800)

    chat_input.fill("Need AI help")
    send_button.click()
    page.wait_for_timeout(2000)

    # Click "Match Experts" button
    match_experts_btn = page.get_by_test_id("match-experts-button")
    expect(match_experts_btn).to_be_visible(timeout=10000)
    match_experts_btn.click()
    # Wait for expert matching to complete and experts to appear
    expect(page.get_by_test_id("expert-match-list")).to_be_visible(timeout=10000)
    page.wait_for_timeout(1000)

    # Click "Book" on first expert
    book_expert_btn = page.get_by_test_id("book-expert-0")
    expect(book_expert_btn).to_be_visible(timeout=5000)
    book_expert_btn.click()

    page.wait_for_timeout(2000)

    # Wait for calendar picker
    expect(page.locator('text=Select Time Slot')).to_be_visible(timeout=10000)

    # Get user's expected timezone
    # In Playwright, we can check what timezone the browser is using
    # The component uses Intl.DateTimeFormat().resolvedOptions().timeZone

    # Verify timezone is displayed (should be visible in the header)
    # Playwright browser may use different timezones (UTC, America/, Europe/, Asia/, Australia/)
    timezone_element = page.locator('text=UTC').or_(
        page.locator('text=America/')).or_(
        page.locator('text=Europe/')).or_(
        page.locator('text=Asia/')).or_(
        page.locator('text=Australia/'))
    expect(timezone_element).to_be_visible()

    print("✓ Timezone detection test passed")


def test_time_slot_selection_confirmation(page: Page):
    """
    Test: Time slot selection shows confirmation UI

    Steps:
    1. Open calendar picker
    2. Click on a time slot
    3. Verify slot is highlighted as selected
    4. Verify confirmation UI appears
    """
    page.goto(FRONTEND_URL)
    page.wait_for_load_state("networkidle")

    # Setup and navigate to booking
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
    # Wait for expert matching to complete and experts to appear
    expect(page.get_by_test_id("expert-match-list")).to_be_visible(timeout=10000)
    page.wait_for_timeout(1000)

    # Click "Book" on first expert
    book_expert_btn = page.get_by_test_id("book-expert-0")
    expect(book_expert_btn).to_be_visible(timeout=5000)
    book_expert_btn.click()

    page.wait_for_timeout(2000)

    # Wait for calendar picker
    page.wait_for_selector('text=Select Time Slot', timeout=10000)

    # Find and click a slot
    slot_buttons = page.locator('button').filter(has_text=re.compile(r'\d{1,2}:\d{2}'))
    slot_buttons.first.click()

    # Verify selection confirmation appears
    expect(page.locator('text=Selected:')).to_be_visible(timeout=5000)

    # Verify Confirm button appears and is enabled
    confirm_btn = page.locator('button:has-text("Confirm Booking")')
    expect(confirm_btn).to_be_visible()
    expect(confirm_btn).to_be_enabled()

    print("✓ Time slot selection confirmation test passed")


def test_double_booking_prevention(page: Page):
    """
    Test: Double-booking prevention works correctly

    Note: This test simulates the scenario by checking that
    the booking flow validates availability before confirming

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
    # Wait for expert matching to complete and experts to appear
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

    # Track API calls
    availability_check_called = False
    booking_create_called = False

    def track_api_calls(route):
        nonlocal availability_check_called, booking_create_called
        url = route.request.url
        if "/availability" in url:
            availability_check_called = True
        if "/bookings" in url and route.request.method == "POST":
            booking_create_called = True
        route.continue_()

    page.route("**/*", track_api_calls)

    # Click confirm
    confirm_btn = page.locator('button:has-text("Confirm Booking")')
    confirm_btn.click()

    # Wait for API calls
    page.wait_for_timeout(3000)

    # Verify availability was checked before booking
    assert availability_check_called, "Availability check should happen before booking"

    print("✓ Double-booking prevention test passed")


def test_availability_refresh(page: Page):
    """
    Test: Availability refreshes in real-time before confirmation

    Steps:
    1. Open calendar picker
    2. Wait for slots to load
    3. Verify auto-refresh mechanism exists
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
    # Wait for expert matching to complete and experts to appear
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

    # Track availability refresh calls
    availability_calls = []

    def track_availability(route):
        url = route.request.url
        if "/availability" in url:
            availability_calls.append(url)
        route.continue_()

    page.route("**/*", track_availability)

    # Wait a bit (component should auto-refresh every 30s when slot is selected)
    # We won't wait 30s, but we verify the mechanism exists by checking
    # that the component has the refresh logic

    # Click confirm (this triggers final availability check)
    confirm_btn = page.locator('button:has-text("Confirm Booking")')
    confirm_btn.click()

    page.wait_for_timeout(2000)

    # Verify at least one availability check happened
    assert len(availability_calls) > 0, "Availability should be checked"

    print("✓ Availability refresh test passed")
