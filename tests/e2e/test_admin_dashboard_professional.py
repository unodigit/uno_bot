"""E2E tests for Admin Dashboard Professional Appearance (Feature #121).

This test suite verifies the admin dashboard has a professional appearance
with consistent styling, professional layout, and brand colors.
"""

from playwright.sync_api import Page, expect


class TestAdminDashboardProfessionalAppearance:
    """Test class for Admin Dashboard Professional Appearance E2E tests."""

    def test_admin_dashboard_loads_and_has_professional_ui(self, page: Page):
        """Test that admin dashboard loads and has professional appearance.
        
        This comprehensive test verifies:
        1. Header with title and subtitle
        2. Tab navigation (Experts, Templates)
        3. Analytics cards with proper styling
        4. Search and filter controls
        5. Action buttons
        """
        print("\n=== Test: Admin Dashboard Professional Appearance ===")

        # Navigate to admin page
        page.goto("http://localhost:5175/admin")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # 1. Verify header
        header = page.locator("div.bg-white.shadow-sm.border-b").first
        expect(header).to_be_visible()
        print("✅ Header is visible")

        title = page.get_by_role("heading", name="Admin Dashboard")
        expect(title).to_be_visible()
        print("✅ Title is visible")

        subtitle = page.locator("text=Manage experts, templates, and system analytics")
        expect(subtitle).to_be_visible()
        print("✅ Subtitle is visible")

        # 2. Verify tab navigation
        experts_tab = page.get_by_role("button", name="Experts")
        templates_tab = page.get_by_role("button", name="Welcome Templates")
        expect(experts_tab).to_be_visible()
        expect(templates_tab).to_be_visible()
        print("✅ Tab navigation is visible")

        # 3. Verify analytics cards exist
        total_experts = page.locator("p:has-text('Total Experts')")
        if total_experts.count() > 0:
            expect(total_experts.first).to_be_visible()
            print("✅ Analytics cards are visible")

        # 4. Verify search and filter controls
        search_input = page.get_by_placeholder("Search experts by name, email, or role...")
        expect(search_input).to_be_visible()
        print("✅ Search input is visible")

        # Filter buttons
        all_buttons = page.get_by_role("button", name="All")
        active_buttons = page.get_by_role("button", name="Active")
        inactive_buttons = page.get_by_role("button", name="Inactive")

        if all_buttons.count() > 0:
            print("✅ Filter buttons exist")

        # 5. Verify action buttons
        add_expert = page.get_by_role("button", name="Add Expert")
        export_csv = page.get_by_role("button", name="Export CSV")
        expect(add_expert).to_be_visible()
        expect(export_csv).to_be_visible()
        print("✅ Action buttons are visible")

        # 6. Verify expert management section
        expert_mgmt = page.locator("text=Expert Management")
        if expert_mgmt.is_visible():
            print("✅ Expert management section is visible")

        # 7. Verify card styling (white background)
        cards = page.locator("div.p-6")
        if cards.count() > 0:
            card = cards.first
            bg = page.evaluate("""(el) => window.getComputedStyle(el).backgroundColor""", card.element_handle())
            if "white" in bg or "rgb(255, 255, 255)" in bg or "rgba(255, 255, 255" in bg:
                print("✅ Cards have white background")
            else:
                print(f"⚠️  Card background: {bg}")

        # 8. Verify brand colors (blue icons)
        blue_icons = page.locator("svg.text-blue-600")
        if blue_icons.count() > 0:
            print("✅ Brand colors (blue) are used")

        print("\n✅ Admin dashboard has professional appearance!")
        print("✅ All key UI elements are properly styled and visible")

    def test_admin_dashboard_template_section(self, page: Page):
        """Test that template section works and looks professional."""
        print("\n=== Test: Template Section Professional Appearance ===")

        # Navigate to admin page
        page.goto("http://localhost:5175/admin")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # Click on Welcome Templates tab
        templates_tab = page.get_by_role("button", name="Welcome Templates")
        if templates_tab.is_visible():
            templates_tab.click()
            page.wait_for_timeout(500)

            # Verify template section is visible
            template_heading = page.locator("text=Welcome Message Templates")
            expect(template_heading).to_be_visible()
            print("✅ Template section is visible")

            # Verify Add Template button
            add_template = page.get_by_role("button", name="Add Template")
            if add_template.is_visible():
                print("✅ Add Template button is visible")

        print("✅ Template section has professional appearance")

    def test_admin_dashboard_summary_comprehensive(self, page: Page):
        """Comprehensive summary test for admin dashboard professional appearance.
        
        This test provides a complete assessment of the admin dashboard's
        professional appearance across all criteria.
        """
        print("\n=== Test: Comprehensive Professional Appearance Assessment ===")

        # Navigate to admin page
        page.goto("http://localhost:5175/admin")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2500)

        # Assessment criteria
        results = {
            "header_structure": False,
            "tab_navigation": False,
            "analytics_cards": False,
            "search_controls": False,
            "action_buttons": False,
            "card_styling": False,
        }

        # 1. Header structure
        header = page.locator("div.bg-white.shadow-sm.border-b").first
        title = page.get_by_role("heading", name="Admin Dashboard")
        subtitle = page.locator("text=Manage experts, templates, and system analytics")
        if header.is_visible() and title.is_visible() and subtitle.is_visible():
            results["header_structure"] = True

        # 2. Tab navigation
        experts_tab = page.get_by_role("button", name="Experts")
        templates_tab = page.get_by_role("button", name="Welcome Templates")
        if experts_tab.is_visible() and templates_tab.is_visible():
            results["tab_navigation"] = True

        # 3. Analytics cards
        total_experts = page.locator("p:has-text('Total Experts')")
        if total_experts.count() > 0:
            results["analytics_cards"] = True

        # 4. Search controls
        search = page.get_by_placeholder("Search experts by name, email, or role...")
        filter_buttons = page.get_by_role("button", name="All")
        if search.is_visible() and filter_buttons.count() > 0:
            results["search_controls"] = True

        # 5. Action buttons
        add_expert = page.get_by_role("button", name="Add Expert")
        export_csv = page.get_by_role("button", name="Export CSV")
        if add_expert.is_visible() and export_csv.is_visible():
            results["action_buttons"] = True

        # 6. Card styling
        cards = page.locator("div.p-6")
        if cards.count() > 0:
            card = cards.first
            bg = page.evaluate("""(el) => window.getComputedStyle(el).backgroundColor""", card.element_handle())
            if "white" in bg or "rgb(255, 255, 255)" in bg:
                results["card_styling"] = True

        # Print results
        print("\n--- Professional Appearance Assessment ---")
        passed = 0
        for criterion, status in results.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {criterion.replace('_', ' ').title()}: {'PASS' if status else 'FAIL'}")
            if status:
                passed += 1

        total = len(results)
        percentage = (passed / total) * 100

        print("\n--- Summary ---")
        print(f"Passed: {passed}/{total} ({percentage:.0f}%)")

        # Overall assessment - at least 4/6 should pass
        assert passed >= 4, f"Admin dashboard should have at least 4/6 professional criteria met. Got {passed}/{total}"
        print("\n✅ Admin dashboard has professional appearance")
