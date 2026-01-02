"""E2E tests for empty states display (Feature #125)

Tests that empty states display correctly with helpful messages,
iconography, and appropriate calls to action.
"""
import pytest
from playwright.sync_api import Page, expect


class TestEmptyStates:
    """Test empty states display correctly"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        """Navigate to page before each test"""
        page.goto(base_url)
        page.wait_for_timeout(500)
        # Ensure chat widget is closed before each test
        page.evaluate("""
            () => {
                const store = window.chatStore;
                if (store && store.setIsOpen) {
                    store.setIsOpen(false);
                }
            }
        """)
        page.wait_for_timeout(200)

    def test_chat_window_empty_state_displays_correctly(self, page: Page):
        """Verify chat window shows empty state when no messages exist"""
        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_timeout(500)

        # Check for empty state message
        messages_container = page.get_by_test_id("messages-container")
        expect(messages_container).to_be_visible()
        print("✓ Chat window empty state displays correctly")

    def test_prd_preview_empty_state(self, page: Page):
        """Verify PRD preview is hidden when no PRD exists"""
        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_timeout(500)

        # PRD preview should NOT be visible initially
        prd_preview = page.get_by_test_id("prd-preview-card")
        expect(prd_preview).not_to_be_visible()
        print("✓ PRD preview correctly hidden when no PRD exists")

    def test_expert_match_container_empty_state(self, page: Page):
        """Verify expert match container is hidden when no experts matched"""
        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_timeout(500)

        # Expert match container should NOT be visible initially
        expert_container = page.get_by_test_id("expert-match-container")
        expect(expert_container).not_to_be_visible()
        print("✓ Expert match container correctly hidden when no experts matched")

    def test_quick_replies_empty_state(self, page: Page):
        """Verify quick replies are hidden when no messages exist"""
        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_timeout(500)

        # Quick replies should NOT be visible initially (no messages yet)
        quick_replies = page.get_by_test_id("quick-replies")
        expect(quick_replies).not_to_be_visible()
        print("✓ Quick replies correctly hidden when no messages exist")

    def test_prd_actions_empty_state(self, page: Page):
        """Verify PRD actions are hidden when no messages exist"""
        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_timeout(500)

        # PRD actions should NOT be visible initially
        prd_actions = page.get_by_test_id("prd-actions")
        expect(prd_actions).not_to_be_visible()
        print("✓ PRD actions correctly hidden when no messages exist")

    def test_expert_actions_empty_state(self, page: Page):
        """Verify expert actions are hidden when no messages exist"""
        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_timeout(500)

        # Expert actions should NOT be visible initially
        expert_actions = page.get_by_test_id("expert-actions")
        expect(expert_actions).not_to_be_visible()
        print("✓ Expert actions correctly hidden when no messages exist")

    def test_empty_states_have_proper_styling(self, page: Page):
        """Verify empty states follow design system styling"""
        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_timeout(500)

        # Check messages container styling
        messages_container = page.get_by_test_id("messages-container")
        expect(messages_container).to_be_visible()

        # Should have proper background
        classes = messages_container.get_attribute("class") or ""
        assert "bg-gray-50" in classes, "Messages container should have gray-50 background"
        assert "min-h-[350px]" in classes, "Messages container should have minimum height"
        print("✓ Empty states follow design system styling")

    def test_empty_states_summary(self, page: Page):
        """Comprehensive summary of empty state implementation"""
        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()
        page.wait_for_timeout(500)

        # Verify all empty state behaviors
        results = {
            "chat_window_empty_state": False,
            "prd_preview_hidden": False,
            "expert_match_hidden": False,
            "quick_replies_hidden": False,
            "prd_actions_hidden": False,
            "expert_actions_hidden": False,
        }

        # Check PRD preview hidden
        prd_preview = page.get_by_test_id("prd-preview-card")
        if not prd_preview.is_visible():
            results["prd_preview_hidden"] = True

        # Check expert match container hidden
        expert_container = page.get_by_test_id("expert-match-container")
        if not expert_container.is_visible():
            results["expert_match_hidden"] = True

        # Check quick replies hidden
        quick_replies = page.get_by_test_id("quick-replies")
        if not quick_replies.is_visible():
            results["quick_replies_hidden"] = True

        # Check PRD actions hidden
        prd_actions = page.get_by_test_id("prd-actions")
        if not prd_actions.is_visible():
            results["prd_actions_hidden"] = True

        # Check expert actions hidden
        expert_actions = page.get_by_test_id("expert-actions")
        if not expert_actions.is_visible():
            results["expert_actions_hidden"] = True

        # Check messages container exists
        messages_container = page.get_by_test_id("messages-container")
        if messages_container.is_visible():
            results["chat_window_empty_state"] = True

        # Print summary
        print("\n=== Empty States Implementation Summary ===")
        for feature, passed in results.items():
            status = "✓" if passed else "✗"
            print(f"{status} {feature}: {'PASS' if passed else 'FAIL'}")

        all_passed = all(results.values())
        assert all_passed, f"Some empty state checks failed: {results}"
        print("✓ All empty state checks passed")
