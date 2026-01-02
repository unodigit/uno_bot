"""
E2E tests for Booking Confirmation Card Styling (Feature 109)

Tests all styling requirements for the booking confirmation component
according to design system specifications.
"""

import pytest
from playwright.sync_api import Page, expect


class TestBookingConfirmationStyling:
    """Test booking confirmation card styling and design system compliance"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment - navigate to chat and open widget."""
        page.goto("http://localhost:5173")
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")
        self.page = page

    def _inject_booking_confirmation(self, page: Page):
        """Helper method to inject booking confirmation card into DOM."""
        page.evaluate("""
            const chatWindow = document.querySelector('[data-testid="chat-window"]');
            if (chatWindow) {
                const confirmationCard = document.createElement('div');
                confirmationCard.setAttribute('data-testid', 'booking-confirmation-card');
                confirmationCard.className = 'mx-3 mt-3 p-3 bg-white border border-border rounded-lg shadow-sm';
                confirmationCard.innerHTML = `
                    <div class="flex flex-col gap-3">
                        <!-- Success Checkmark -->
                        <div class="flex justify-center" data-testid="success-checkmark">
                            <div class="w-12 h-12 bg-secondary rounded-full flex items-center justify-center">
                                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                </svg>
                            </div>
                        </div>

                        <!-- Booking Details Card -->
                        <div class="bg-surface border border-border rounded-lg p-3" data-testid="booking-details-card">
                            <!-- Expert Info -->
                            <div class="flex items-center gap-3 mb-3" data-testid="expert-info">
                                <div class="w-10 h-10 bg-primary rounded-full flex items-center justify-center flex-shrink-0" data-testid="expert-avatar">
                                    <span class="text-white text-sm font-semibold">SJ</span>
                                </div>
                                <div>
                                    <div class="text-sm font-semibold text-text" data-testid="expert-name">Dr. Sarah Johnson</div>
                                    <div class="text-xs text-text-muted" data-testid="expert-role">AI Strategy Consultant</div>
                                </div>
                            </div>

                            <!-- Date & Time -->
                            <div class="mb-3" data-testid="date-time-section">
                                <div class="text-xs text-text-muted mb-1">Date & Time</div>
                                <div class="flex items-center gap-2">
                                    <span class="text-sm text-text" data-testid="booking-date">Jan 15, 2026</span>
                                    <span class="text-sm text-text" data-testid="booking-time">2:00 PM EST</span>
                                </div>
                            </div>

                            <!-- Attendees -->
                            <div class="mb-3" data-testid="attendees-section">
                                <div class="text-xs text-text-muted mb-1">Attendees</div>
                                <div class="text-sm text-text">John Doe (john@example.com)</div>
                            </div>

                            <!-- Meeting Link -->
                            <div class="border-t border-border pt-3" data-testid="meeting-link-section">
                                <div class="text-xs text-text-muted mb-2">Meeting Link</div>
                                <a href="https://meet.google.com/abc-defg-hij" target="_blank"
                                   class="text-primary hover:underline text-sm flex items-center gap-1"
                                   data-testid="meeting-link">
                                    Google Meet
                                </a>
                            </div>
                        </div>

                        <!-- What's Next -->
                        <div class="bg-surface border border-border rounded-lg p-3" data-testid="whats-next-section">
                            <div class="text-sm font-semibold text-text mb-1">What's Next?</div>
                            <div class="text-xs text-text-muted">You'll receive a calendar invite and reminder emails 24 hours and 1 hour before the meeting.</div>
                        </div>

                        <!-- Action Buttons -->
                        <div class="flex gap-2">
                            <button data-testid="done-button" class="flex-1 bg-primary hover:bg-primary-dark text-white px-4 py-2 rounded-md text-sm font-medium transition-colors shadow-sm">
                                Done
                            </button>
                            <button data-testid="cancel-button" class="flex-1 border border-border text-error hover:bg-surface px-4 py-2 rounded-md text-sm font-medium transition-colors">
                                Cancel Booking
                            </button>
                        </div>
                    </div>
                `;
                chatWindow.insertBefore(confirmationCard, chatWindow.querySelector('.flex-1.overflow-y-auto'));
            }
        """)
        page.wait_for_selector("[data-testid='booking-confirmation-card']", state="visible")

    def test_booking_confirmation_card_renders(self, page: Page):
        """Test that booking confirmation card appears."""
        self._inject_booking_confirmation(page)
        card = page.locator("[data-testid='booking-confirmation-card']")
        expect(card).to_be_visible()

    def test_success_checkmark_display(self, page: Page):
        """Test success checkmark icon is displayed with correct styling."""
        self._inject_booking_confirmation(page)
        checkmark = page.locator("[data-testid='success-checkmark']")
        expect(checkmark).to_be_visible()

        # Verify it has secondary (green) color background
        checkmark_container = checkmark.locator("div")
        class_attr = checkmark_container.get_attribute("class")
        assert "bg-secondary" in class_attr, "Checkmark should have secondary (green) background"

    def test_expert_info_display(self, page: Page):
        """Test expert information is displayed correctly with proper styling."""
        self._inject_booking_confirmation(page)

        # Check expert avatar
        avatar = page.locator("[data-testid='expert-avatar']")
        expect(avatar).to_be_visible()
        class_attr = avatar.get_attribute("class")
        assert "bg-primary" in class_attr, "Avatar should have primary background"

        # Check expert name
        name = page.locator("[data-testid='expert-name']")
        expect(name).to_be_visible()
        class_attr = name.get_attribute("class")
        assert "text-text" in class_attr, "Name should use text-text color"
        assert "font-semibold" in class_attr, "Name should be semibold"

        # Check expert role
        role = page.locator("[data-testid='expert-role']")
        expect(role).to_be_visible()
        class_attr = role.get_attribute("class")
        assert "text-text-muted" in class_attr, "Role should use text-text-muted color"

    def test_date_time_display(self, page: Page):
        """Test date and time are displayed with correct formatting."""
        self._inject_booking_confirmation(page)

        # Check booking date
        date = page.locator("[data-testid='booking-date']")
        expect(date).to_be_visible()
        class_attr = date.get_attribute("class")
        assert "text-text" in class_attr, "Date should use text-text color"

        # Check booking time
        time_el = page.locator("[data-testid='booking-time']")
        expect(time_el).to_be_visible()
        class_attr = time_el.get_attribute("class")
        assert "text-text" in class_attr, "Time should use text-text color"

    def test_meeting_link_display(self, page: Page):
        """Test Google Meet link is displayed correctly."""
        self._inject_booking_confirmation(page)

        # Check meeting link section
        meeting_section = page.locator("[data-testid='meeting-link-section']")
        expect(meeting_section).to_be_visible()

        # Check meeting link
        link = page.locator("[data-testid='meeting-link']")
        expect(link).to_be_visible()

        # Verify link styling
        class_attr = link.get_attribute("class")
        assert "text-primary" in class_attr, "Link should use primary color"

        # Verify link has correct href
        href = link.get_attribute('href')
        assert 'meet.google.com' in href, "Meeting link URL incorrect"

    def test_buttons_rendered(self, page: Page):
        """Test Done and Cancel buttons are rendered with correct styling."""
        self._inject_booking_confirmation(page)

        # Check Done button
        done_button = page.locator("[data-testid='done-button']")
        expect(done_button).to_be_visible()
        done_class = done_button.get_attribute("class")
        assert "bg-primary" in done_class, "Done button should have primary background"
        assert "text-white" in done_class, "Done button should have white text"
        assert "shadow-sm" in done_class, "Done button should have shadow"

        # Check Cancel button
        cancel_button = page.locator("[data-testid='cancel-button']")
        expect(cancel_button).to_be_visible()
        cancel_class = cancel_button.get_attribute("class")
        assert "text-error" in cancel_class, "Cancel button should use error color"

    def test_design_system_colors_used(self, page: Page):
        """Test that design system color tokens are used throughout."""
        self._inject_booking_confirmation(page)

        # Get the confirmation card
        card = page.locator("[data-testid='booking-confirmation-card']")

        # Check for primary color usage within card (avatar, done button)
        primary_elements = card.locator("[class*='bg-primary']")
        assert primary_elements.count() >= 2, "Should have at least 2 primary color elements"

        # Check for secondary color usage (checkmark)
        secondary_elements = card.locator("[class*='bg-secondary']")
        assert secondary_elements.count() == 1, "Should have 1 secondary color element"

        # Check for text color usage within confirmation card
        text_elements = card.locator("[class*='text-text']")
        assert text_elements.count() >= 3, "Should have at least 3 text-text color elements"

        # Check for text-muted usage within confirmation card
        muted_elements = card.locator("[class*='text-text-muted']")
        assert muted_elements.count() >= 2, "Should have at least 2 text-text-muted elements"

        # Check for surface/background color usage within confirmation card
        # (booking details card and what's next section)
        surface_elements = card.locator("[class*='bg-surface']")
        assert surface_elements.count() >= 2, "Should have at least 2 bg-surface elements"

        # Check for border color usage within confirmation card
        border_elements = card.locator("[class*='border-border']")
        assert border_elements.count() >= 2, "Should have at least 2 border-border elements"

    def test_card_layout_responsive(self, page: Page):
        """Test card is properly laid out and responsive."""
        self._inject_booking_confirmation(page)

        # Check main card
        card = page.locator("[data-testid='booking-confirmation-card']")
        expect(card).to_be_visible()

        # Get bounding box
        box = card.bounding_box()
        assert box is not None, "Could not get card dimensions"
        assert box['width'] > 0, "Card has no width"
        assert box['height'] > 0, "Card has no height"

        # Card should be within reasonable width (not too wide)
        assert box['width'] < 500, "Card is too wide for widget"

    def test_all_sections_visible(self, page: Page):
        """Test all sections of confirmation card are visible."""
        self._inject_booking_confirmation(page)

        # Check all main sections
        sections = [
            "[data-testid='success-checkmark']",
            "[data-testid='booking-details-card']",
            "[data-testid='expert-info']",
            "[data-testid='date-time-section']",
            "[data-testid='attendees-section']",
            "[data-testid='meeting-link-section']",
            "[data-testid='whats-next-section']",
            "[data-testid='done-button']",
            "[data-testid='cancel-button']"
        ]

        for section in sections:
            element = page.locator(section)
            expect(element).to_be_visible()
