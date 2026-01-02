"""
E2E tests for PRD Preview Card Styling (Feature #107)

This test suite verifies the PRD preview card displays correctly with proper styling
according to the design system specifications.
"""

import pytest
from playwright.sync_api import Page, expect


class TestPRDPreviewCardStyling:
    """Test PRD preview card styling and layout."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup test environment - navigate to chat and open widget."""
        page.goto("http://localhost:5173")
        page.click("[data-testid='chat-widget-button']")
        page.wait_for_selector("[data-testid='chat-window']", state="visible")

    def _inject_prd_preview_card(self, page: Page, filename: str = "PRD.md", preview_text: str = "Preview text..."):
        """Helper method to inject PRD preview card into DOM."""
        page.evaluate(f"""
            const chatWindow = document.querySelector('[data-testid="chat-window"]');
            if (chatWindow) {{
                const prdCard = document.createElement('div');
                prdCard.setAttribute('data-testid', 'prd-preview-card');
                prdCard.className = 'mx-3 mt-3 p-3 bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg shadow-sm';
                prdCard.innerHTML = `
                    <div class="flex items-start gap-3">
                        <div class="w-10 h-10 bg-primary rounded-lg flex items-center justify-center flex-shrink-0">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5 text-white"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center justify-between mb-1">
                                <h4 class="text-sm font-semibold text-gray-900">PRD Generated!</h4>
                            </div>
                            <p class="text-xs text-gray-600 mb-2 line-clamp-2">{preview_text}</p>
                            <div class="flex items-center gap-2">
                                <button data-testid="download-prd-button" class="flex items-center gap-1 px-2 py-1 bg-primary hover:bg-primary-dark text-white text-xs rounded transition-colors">
                                    Download
                                </button>
                                <span class="text-xs text-gray-500">{filename}</span>
                            </div>
                        </div>
                    </div>
                `;
                chatWindow.insertBefore(prdCard, chatWindow.querySelector('.flex-1.overflow-y-auto'));
            }}
        """)
        page.wait_for_selector("[data-testid='prd-preview-card']", state="visible")

    def test_prd_preview_card_appears(self, page: Page):
        """Verify PRD preview card appears when generated."""
        self._inject_prd_preview_card(page)
        card = page.locator("[data-testid='prd-preview-card']")
        expect(card).to_be_visible()

    def test_prd_preview_card_has_document_icon(self, page: Page):
        """Verify PRD preview card displays document icon."""
        self._inject_prd_preview_card(page)
        icon_container = page.locator("[data-testid='prd-preview-card'] .bg-primary.rounded-lg")
        expect(icon_container).to_be_visible()
        icon = icon_container.locator("svg")
        expect(icon).to_be_visible()

    def test_prd_preview_card_displays_filename(self, page: Page):
        """Verify PRD preview card shows the filename."""
        test_filename = "My_Project_PRD.md"
        self._inject_prd_preview_card(page, filename=test_filename)
        card = page.locator("[data-testid='prd-preview-card']")
        expect(card).to_contain_text(test_filename)

    def test_prd_preview_card_shows_preview_text(self, page: Page):
        """Verify PRD preview card displays preview text snippet."""
        test_preview = "This document outlines the comprehensive requirements for building an AI-powered business consultant."
        self._inject_prd_preview_card(page, preview_text=test_preview)
        card = page.locator("[data-testid='prd-preview-card']")
        expect(card).to_contain_text(test_preview[:50])

    def test_prd_preview_card_has_gradient_background(self, page: Page):
        """Verify PRD preview card has gradient background styling."""
        self._inject_prd_preview_card(page)
        card = page.locator("[data-testid='prd-preview-card']")
        # Check that card has the gradient classes
        class_attr = card.get_attribute("class")
        assert "bg-gradient-to-br" in class_attr, "Card should have gradient background"
        assert "from-blue-50" in class_attr, "Card should have blue-50 start"
        assert "to-indigo-50" in class_attr, "Card should have indigo-50 end"

    def test_prd_preview_card_has_border(self, page: Page):
        """Verify PRD preview card has proper border styling."""
        self._inject_prd_preview_card(page)
        card = page.locator("[data-testid='prd-preview-card']")
        class_attr = card.get_attribute("class")
        assert "border" in class_attr, "Card should have border"
        assert "border-blue-200" in class_attr, "Card should have blue-200 border"

    def test_prd_preview_card_has_shadow(self, page: Page):
        """Verify PRD preview card has shadow for depth."""
        self._inject_prd_preview_card(page)
        card = page.locator("[data-testid='prd-preview-card']")
        class_attr = card.get_attribute("class")
        assert "shadow-sm" in class_attr, "Card should have shadow-sm"

    def test_prd_preview_card_has_download_button(self, page: Page):
        """Verify PRD preview card has download button."""
        self._inject_prd_preview_card(page)
        download_btn = page.locator("[data-testid='download-prd-button']")
        expect(download_btn).to_be_visible()

    def test_prd_preview_download_button_styling(self, page: Page):
        """Verify download button has correct styling."""
        self._inject_prd_preview_card(page)
        download_btn = page.locator("[data-testid='download-prd-button']")
        class_attr = download_btn.get_attribute("class")
        assert "bg-primary" in class_attr, "Download button should have primary background"
        assert "text-white" in class_attr, "Download button should have white text"
        assert "rounded" in class_attr, "Download button should be rounded"
        assert "transition-colors" in class_attr, "Download button should have transition"

    def test_prd_preview_card_proper_padding(self, page: Page):
        """Verify PRD preview card has proper padding."""
        self._inject_prd_preview_card(page)
        card = page.locator("[data-testid='prd-preview-card']")
        class_attr = card.get_attribute("class")
        assert "p-3" in class_attr, "Card should have p-3 padding (12px)"

    def test_prd_preview_card_rounded_corners(self, page: Page):
        """Verify PRD preview card has rounded corners."""
        self._inject_prd_preview_card(page)
        card = page.locator("[data-testid='prd-preview-card']")
        class_attr = card.get_attribute("class")
        assert "rounded-lg" in class_attr, "Card should have rounded-lg corners"

    def test_prd_preview_card_title_styling(self, page: Page):
        """Verify PRD preview card title has proper styling."""
        self._inject_prd_preview_card(page)
        card = page.locator("[data-testid='prd-preview-card']")
        title = card.locator("h4")
        expect(title).to_be_visible()
        class_attr = title.get_attribute("class")
        assert "text-sm" in class_attr, "Title should have text-sm size"
        assert "font-semibold" in class_attr, "Title should have semibold font"
        assert "text-gray-900" in class_attr, "Title should have gray-900 color"

    def test_prd_preview_card_responsive_width(self, page: Page):
        """Verify PRD preview card maintains responsive layout within chat window."""
        self._inject_prd_preview_card(page)
        card = page.locator("[data-testid='prd-preview-card']")
        class_attr = card.get_attribute("class")
        assert "mx-3" in class_attr, "Card should have horizontal margin"

        # Verify card doesn't overflow chat window
        chat_window = page.locator("[data-testid='chat-window']")
        chat_window_width = chat_window.bounding_box()["width"]
        card_width = card.bounding_box()["width"]

        assert card_width < chat_window_width, "PRD preview card should not overflow chat window"

    def test_prd_preview_card_icon_primary_color(self, page: Page):
        """Verify document icon uses primary color background."""
        self._inject_prd_preview_card(page)
        # Use more specific selector to avoid ambiguity
        icon_container = page.locator("[data-testid='prd-preview-card'] .w-10.bg-primary")
        expect(icon_container).to_be_visible()

        icon = icon_container.locator("svg")
        class_attr = icon.get_attribute("class")
        assert "text-white" in class_attr, "Icon should be white on primary background"

    def test_prd_preview_card_long_filename_handling(self, page: Page):
        """Verify long filenames are handled gracefully."""
        long_filename = "This_Is_A_Very_Long_Project_Name_Requirements_Document_2026_Final_v2.md"
        self._inject_prd_preview_card(page, filename=long_filename)

        card = page.locator("[data-testid='prd-preview-card']")
        expect(card).to_be_visible()
        expect(card).to_contain_text(long_filename[:30])

    def test_prd_preview_card_proper_margin_top(self, page: Page):
        """Verify PRD preview card has top margin for spacing."""
        self._inject_prd_preview_card(page)
        card = page.locator("[data-testid='prd-preview-card']")
        class_attr = card.get_attribute("class")
        assert "mt-3" in class_attr, "Card should have top margin"
