from playwright.sync_api import Page, expect


class TestAdminExpertEditing:
    """Test admin expert profile editing functionality."""

    def test_admin_can_edit_existing_expert_profiles(self, page: Page):
        """Test that admin can edit existing expert profiles."""
        # Navigate to admin page
        page.goto("http://localhost:5173/admin")
        page.wait_for_load_state("networkidle")

        # Click login to show admin dashboard
        login_button = page.get_by_role("button", name="Login")
        if login_button.is_visible():
            login_button.click()

        # Now verify admin dashboard is visible
        admin_title = page.get_by_role("heading", name="Admin Dashboard")
        expect(admin_title).to_be_visible()

        # Verify experts list is loaded
        experts_section = page.locator("text=Expert Management")
        expect(experts_section).to_be_visible()

        # Wait for experts to load (should see at least one expert)
        page.wait_for_selector('[data-testid^="expert-card-"]', timeout=10000)

        # Get the first expert card
        first_expert_card = page.locator('[data-testid^="expert-card-"]').first
        expect(first_expert_card).to_be_visible()

        # Hover over expert card to show action buttons
        first_expert_card.hover()

        # Click edit button
        edit_button = first_expert_card.locator('button:has-text("Edit")')
        expect(edit_button).to_be_visible()
        edit_button.click()

        # Verify edit form is visible
        edit_form = page.locator("text=Edit Expert")
        expect(edit_form).to_be_visible()

        # Get original values
        name_input = page.get_by_placeholder("Expert name")
        original_name = name_input.input_value()
        original_email = page.get_by_placeholder("expert@example.com").input_value()
        original_role = page.get_by_placeholder("e.g., Senior Developer, AI Consultant").input_value()

        # Modify the form fields
        test_suffix = "_test_edit"
        new_name = original_name + test_suffix
        new_role = original_role + test_suffix

        name_input.clear()
        name_input.fill(new_name)

        role_input = page.get_by_placeholder("e.g., Senior Developer, AI Consultant")
        role_input.clear()
        role_input.fill(new_role)

        # Save the changes
        save_button = page.get_by_role("button", name="Save Changes")
        expect(save_button).to_be_visible()
        save_button.click()

        # Wait for form to close and changes to be saved
        page.wait_for_selector("text=Edit Expert", state="hidden", timeout=5000)

        # Verify the expert list shows updated information
        page.wait_for_timeout(1000)  # Allow time for UI update

        # Check if the updated name appears in the expert list
        updated_expert_card = page.locator(f'text="{new_name}"')
        expect(updated_expert_card).to_be_visible()

        # Verify the changes were persisted by reloading the page
        page.reload()
        page.wait_for_load_state("networkidle")

        # Navigate back to admin dashboard
        page.goto("http://localhost:5173/admin")
        page.wait_for_load_state("networkidle")

        # Verify the edited expert name is still visible
        final_expert_card = page.locator(f'text="{new_name}"')
        expect(final_expert_card).to_be_visible()

        print("✅ Successfully verified admin expert editing functionality")
        print(f"✅ Edited expert name from '{original_name}' to '{new_name}'")
        print("✅ Changes persisted after page reload")

    def test_admin_edit_form_validation(self, page: Page):
        """Test admin expert edit form validation."""
        # Navigate to admin dashboard
        page.goto("http://localhost:5173/admin")
        page.wait_for_load_state("networkidle")

        # Wait for experts to load
        page.wait_for_selector('[data-testid^="expert-card-"]', timeout=10000)

        # Get the first expert card and edit it
        first_expert_card = page.locator('[data-testid^="expert-card-"]').first
        first_expert_card.hover()
        edit_button = first_expert_card.locator('button:has-text("Edit")')
        edit_button.click()

        # Verify edit form is visible
        edit_form = page.locator("text=Edit Expert")
        expect(edit_form).to_be_visible()

        # Clear required fields to test validation
        name_input = page.get_by_placeholder("Expert name")
        original_name = name_input.input_value()
        name_input.clear()

        # Try to save with empty required field
        save_button = page.get_by_role("button", name="Save Changes")
        save_button.click()

        # Form should remain open due to validation error
        edit_form_visible = page.locator("text=Edit Expert").is_visible()
        assert edit_form_visible, "Form should remain open when validation fails"

        # Restore the name and save
        name_input.fill(original_name)
        save_button.click()

        # Form should close after successful save
        page.wait_for_selector("text=Edit Expert", state="hidden", timeout=5000)

        print("✅ Successfully verified admin edit form validation")

    def test_admin_edit_cancel_functionality(self, page: Page):
        """Test admin expert edit cancel functionality."""
        # Navigate to admin dashboard
        page.goto("http://localhost:5173/admin")
        page.wait_for_load_state("networkidle")

        # Wait for experts to load
        page.wait_for_selector('[data-testid^="expert-card-"]', timeout=10000)

        # Get the first expert card and edit it
        first_expert_card = page.locator('[data-testid^="expert-card-"]').first
        first_expert_card.hover()
        edit_button = first_expert_card.locator('button:has-text("Edit")')
        edit_button.click()

        # Verify edit form is visible
        edit_form = page.locator("text=Edit Expert")
        expect(edit_form).to_be_visible()

        # Modify the form fields
        name_input = page.get_by_placeholder("Expert name")
        original_name = name_input.input_value()
        test_suffix = "_should_not_save"
        name_input.clear()
        name_input.fill(original_name + test_suffix)

        # Click cancel
        cancel_button = page.get_by_role("button", name="Cancel")
        cancel_button.click()

        # Form should close
        page.wait_for_selector("text=Edit Expert", state="hidden", timeout=5000)

        # Verify the original name is still visible (changes were not saved)
        original_expert_card = page.locator(f'text="{original_name}"')
        expect(original_expert_card).to_be_visible()

        # Verify the modified name is not visible
        modified_expert_card = page.locator(f'text="{original_name + test_suffix}"')
        assert not modified_expert_card.is_visible(), "Modified name should not be visible"

        print("✅ Successfully verified admin edit cancel functionality")
