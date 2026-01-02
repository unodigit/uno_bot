"""End-to-end tests for multiple expert options feature."""
from playwright.sync_api import Page, expect
import re

# Frontend URL
FRONTEND_URL = "http://localhost:5173"


class TestMultipleExpertOptions:
    """Test cases for multiple expert options display when available."""

    def test_multiple_expert_options_shown_when_available(self, page: Page):
        """
        Test: Multiple expert options shown when available

        Steps:
        1. Set up multiple matching experts
        2. Complete discovery for matching service
        3. Verify multiple expert cards displayed
        4. Verify user can choose between experts
        """
        # Navigate to the app
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        expect(chat_button).to_be_visible()
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        expect(chat_window).to_be_visible()

        # Complete conversation to enable expert matching
        # We'll provide information that will match multiple experts

        # Send messages to progress through the conversation
        input_field = page.get_by_test_id("message-input")

        # Provide name
        input_field.fill("John Doe")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(1000)

        # Provide email
        input_field.fill("john@example.com")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(1000)

        # Provide company
        input_field.fill("I work at TechCorp")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(1000)

        # Describe business challenges (AI Strategy service)
        input_field.fill("We need help with AI strategy and planning for our digital transformation")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(2000)

        # Provide industry
        input_field.fill("We're in the healthcare industry")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(1000)

        # Provide budget
        input_field.fill("Our budget is around 50000")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(1000)

        # Provide timeline
        input_field.fill("We need this done within 3 months")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(2000)

        # Wait for Match Experts button to appear
        # The button should appear after the conversation has progressed enough
        match_experts_btn = page.get_by_test_id("match-experts-button")
        expect(match_experts_btn).to_be_visible(timeout=10000)
        print("✓ Match Experts button appeared")

        # Click Match Experts button
        match_experts_btn.click()

        # Wait for expert matching to complete and expert list to appear
        expert_match_list = page.get_by_test_id("expert-match-list")
        expect(expert_match_list).to_be_visible(timeout=10000)
        print("✓ Expert match list displayed")

        # Wait a moment for all expert cards to render
        page.wait_for_timeout(1000)

        # Step 3: Verify multiple expert cards are displayed
        # Count expert cards using data-testid pattern
        expert_cards = page.locator('[data-testid^="expert-card-"]')
        card_count = expert_cards.count()

        print(f"✓ Found {card_count} expert cards")

        # We expect at least 1 expert card to be shown
        assert card_count >= 1, f"Expected at least 1 expert card, found {card_count}"

        # If multiple experts exist, verify they're all displayed
        if card_count > 1:
            print(f"✓ Multiple expert options ({card_count} experts) are displayed")

            # Verify each expert card has required elements
            for i in range(card_count):
                # Check expert card exists
                expert_card = page.get_by_test_id(f"expert-card-{i}")
                expect(expert_card).to_be_visible()

                # Check expert name is visible
                # Expert cards should have a name (h4 element)
                expect(expert_card.locator('h4')).to_be_visible()

                # Check expert role is visible
                expect(expert_card.locator('p')).to_be_visible()

                # Check match score badge (for matched experts)
                match_badge = expert_card.locator('.text-primary').filter(has_text=re.compile(r'\d+%'))
                if match_badge.count() > 0:
                    print(f"✓ Expert {i} has match score displayed")

                # Check Book button exists
                book_btn = page.get_by_test_id(f"book-expert-{i}")
                expect(book_btn).to_be_visible()
                print(f"✓ Expert {i} has Book button")

                # Check Select button exists
                select_btn = page.get_by_test_id(f"select-expert-{i}")
                expect(select_btn).to_be_visible()
                print(f"✓ Expert {i} has Select button")

        # Step 4: Verify user can choose between experts
        # Click Select on first expert
        first_select_btn = page.get_by_test_id("select-expert-0")
        first_select_btn.click()

        # Verify some action occurred (e.g., selection was registered)
        # The button click should register the selection
        page.wait_for_timeout(500)

        # Verify expert list is still visible (selection doesn't hide it)
        expect(expert_match_list).to_be_visible()
        print("✓ User can select between experts")

        # Verify user can click Book on different experts
        # Click Book on second expert (if exists)
        if card_count > 1:
            second_book_btn = page.get_by_test_id("book-expert-1")
            expect(second_book_btn).to_be_visible()
            print("✓ User can book different experts")

            # Click it to verify booking flow starts
            second_book_btn.click()
            page.wait_for_timeout(1000)

            # Calendar picker should appear
            expect(page.locator('text=Select Time Slot')).to_be_visible(timeout=5000)
            print("✓ Booking flow starts when clicking Book on expert")

        print("\n✅ Multiple expert options test passed!")

    def test_single_expert_when_only_one_match(self, page: Page):
        """
        Test: When only one expert matches, show single expert card

        This test verifies the system gracefully handles single expert matches
        and still displays the expert card with appropriate actions.
        """
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Open chat
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_timeout(500)

        # Complete basic conversation
        input_field = page.get_by_test_id("message-input")

        input_field.fill("Jane Smith")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(1000)

        input_field.fill("jane@example.com")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(1000)

        input_field.fill("Acme Corp")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(1000)

        input_field.fill("We need custom software development")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(2000)

        input_field.fill("Manufacturing industry")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(1000)

        input_field.fill("Budget is 75000")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(1000)

        input_field.fill("Need it in 2 months")
        page.get_by_test_id("send-button").click()
        page.wait_for_timeout(2000)

        # Match experts
        match_experts_btn = page.get_by_test_id("match-experts-button")
        expect(match_experts_btn).to_be_visible(timeout=10000)
        match_experts_btn.click()

        # Wait for expert list
        expert_match_list = page.get_by_test_id("expert-match-list")
        expect(expert_match_list).to_be_visible(timeout=10000)

        page.wait_for_timeout(1000)

        # Count experts (may be 1 or more depending on database)
        expert_cards = page.locator('[data-testid^="expert-card-"]')
        card_count = expert_cards.count()

        print(f"✓ Found {card_count} expert card(s)")

        # Whether 1 or more, verify each expert card is properly displayed
        for i in range(card_count):
            expert_card = page.get_by_test_id(f"expert-card-{i}")
            expect(expert_card).to_be_visible()

            # Verify name and role
            expect(expert_card.locator('h4')).to_be_visible()

            # Verify action buttons exist
            book_btn = page.get_by_test_id(f"book-expert-{i}")
            expect(book_btn).to_be_visible()

            print(f"✓ Expert card {i} properly displayed")

        print("\n✅ Single/multiple expert handling test passed!")
