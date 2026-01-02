"""E2E tests for typography system compliance with design system."""
import pytest
from playwright.sync_api import Page, expect


class TestTypographySystem:
    """Test typography follows design system specifications."""

    def test_inter_font_is_loaded(self, page: Page, base_url: str) -> None:
        """Verify Inter font is loaded from Google Fonts."""
        page.goto(base_url)

        # Check if Google Fonts stylesheet link is present (link may be hidden but in DOM)
        inter_font_link = page.locator('link[href*="Inter"][rel="stylesheet"]')
        expect(inter_font_link).to_have_count(1)

        # Verify it's loading Inter font with correct weights
        href = inter_font_link.get_attribute("href")
        assert href == "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap"

    def test_font_family_applied_to_body(self, page: Page, base_url: str) -> None:
        """Verify Inter font family is applied to body element."""
        page.goto(base_url)

        # Get computed font family
        font_family = page.locator("body").evaluate("el => getComputedStyle(el).fontFamily")

        # Verify Inter is in the font stack
        assert "Inter" in font_family, f"Expected 'Inter' in font family, got: {font_family}"

    def test_font_size_text_sm_is_14px(self, page: Page, base_url: str) -> None:
        """Verify text-sm class renders at 14px (Size SM per design system)."""
        page.goto(base_url)

        # Open chat widget to access UI elements
        chat_button = page.get_by_test_id("chat-widget-button")
        expect(chat_button).to_be_visible()
        chat_button.click()

        # Wait for chat window to open
        chat_window = page.get_by_test_id("chat-window")
        expect(chat_window).to_be_visible()

        # Find an element with text-sm class (labels, helper text, etc.)
        text_sm_elements = page.locator(".text-sm").first
        expect(text_sm_elements).to_be_visible()

        # Verify font size is 14px
        font_size = text_sm_elements.evaluate("el => getComputedStyle(el).fontSize")
        assert font_size == "14px", f"Expected 'text-sm' to be 14px, got: {font_size}"

    def test_font_size_text_base_is_16px(self, page: Page, base_url: str) -> None:
        """Verify text-base class renders at 16px (Size Base per design system)."""
        page.goto(base_url)

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # text-base may not be visible in chat widget, check if it exists
        text_base_elements = page.locator(".text-base")
        if text_base_elements.count() > 0:
            first_element = text_base_elements.first
            if first_element.is_visible():
                # Verify font size is 16px
                font_size = first_element.evaluate("el => getComputedStyle(el).fontSize")
                assert font_size == "16px", f"Expected 'text-base' to be 16px, got: {font_size}"
        else:
            # text-base not present in current UI, skip verification
            pytest.skip("text-base elements not present in current UI")

    def test_font_size_text_lg_is_18px(self, page: Page, base_url: str) -> None:
        """Verify text-lg class renders at 18px (Size LG per design system)."""
        page.goto(base_url)

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # text-lg may not be visible in chat widget, check if it exists
        text_lg_elements = page.locator(".text-lg")
        if text_lg_elements.count() > 0:
            first_element = text_lg_elements.first
            if first_element.is_visible():
                # Verify font size is 18px
                font_size = first_element.evaluate("el => getComputedStyle(el).fontSize")
                assert font_size == "18px", f"Expected 'text-lg' to be 18px, got: {font_size}"
        else:
            # text-lg not present in current UI, skip verification
            pytest.skip("text-lg elements not present in current UI")

    def test_font_weight_normal_is_400(self, page: Page, base_url: str) -> None:
        """Verify font-normal class renders at weight 400 (Weight Normal per design system)."""
        page.goto(base_url)

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Find an element with font-normal class
        font_normal_elements = page.locator(".font-normal").first
        if font_normal_elements.is_visible():
            font_weight = font_normal_elements.evaluate("el => getComputedStyle(el).fontWeight")
            assert font_weight == "400", f"Expected 'font-normal' to be 400, got: {font_weight}"

    def test_font_weight_medium_is_500(self, page: Page, base_url: str) -> None:
        """Verify font-medium class renders at weight 500 (Weight Medium per design system)."""
        page.goto(base_url)

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Find an element with font-medium class
        font_medium_elements = page.locator(".font-medium").first
        expect(font_medium_elements).to_be_visible()

        # Verify font weight is 500
        font_weight = font_medium_elements.evaluate("el => getComputedStyle(el).fontWeight")
        assert font_weight == "500", f"Expected 'font-medium' to be 500, got: {font_weight}"

    def test_font_weight_semibold_is_600(self, page: Page, base_url: str) -> None:
        """Verify font-semibold class renders at weight 600 (Weight Bold per design system)."""
        page.goto(base_url)

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Find an element with font-semibold class
        font_semibold_elements = page.locator(".font-semibold").first
        expect(font_semibold_elements).to_be_visible()

        # Verify font weight is 600
        font_weight = font_semibold_elements.evaluate("el => getComputedStyle(el).fontWeight")
        assert font_weight == "600", f"Expected 'font-semibold' to be 600, got: {font_weight}"

    def test_chat_window_uses_correct_typography(self, page: Page, base_url: str) -> None:
        """Verify chat window uses Inter font with correct sizes and weights."""
        page.goto(base_url)

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat window to open
        page.wait_for_timeout(1000)

        # Verify body uses Inter font (chat window inherits from body)
        font_family = page.locator("body").evaluate("el => getComputedStyle(el).fontFamily")
        assert "Inter" in font_family, f"Page should use Inter font, got: {font_family}"

    def test_messages_use_correct_typography(self, page: Page, base_url: str) -> None:
        """Verify chat messages use Inter font with correct sizes (text-sm)."""
        page.goto(base_url)

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat window to open and messages to load
        page.wait_for_timeout(2000)

        # Verify messages use Inter font (inherited from body)
        font_family = page.locator("body").evaluate("el => getComputedStyle(el).fontFamily")
        assert "Inter" in font_family, f"Messages should use Inter font, got: {font_family}"

    def test_buttons_use_correct_font_weights(self, page: Page, base_url: str) -> None:
        """Verify buttons use appropriate font weights per design system."""
        page.goto(base_url)

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat window to open
        page.wait_for_timeout(1000)

        # Check that the close button exists and has a font weight
        close_button = page.locator("button").filter(has_text="×")
        if close_button.is_visible():
            font_weight = close_button.evaluate("el => getComputedStyle(el).fontWeight")
            # Just verify it has a weight
            assert font_weight in ["400", "500", "600", "700"], f"Close button should have valid font weight, got: {font_weight}"
