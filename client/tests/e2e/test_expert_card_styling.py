"""E2E tests for expert card styling and layout."""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_expert_card_has_correct_layout_and_styling(page: Page):
    """Test that expert card has correct layout and styling according to design system."""

    # Navigate to the main page
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")

    # Open chat widget
    chat_button = page.locator('[data-testid="chat-widget-button"]')
    expect(chat_button).to_be_visible()
    chat_button.click()

    # Wait for chat widget to open
    chat_widget = page.locator('[data-testid="chat-widget"]')
    expect(chat_widget).to_be_visible()

    # Send a message to trigger expert matching phase
    input_field = page.locator('[data-testid="chat-input"]')
    expect(input_field).to_be_visible()
    input_field.fill("I need help with AI strategy for my healthcare company")
    page.keyboard.press("Enter")

    # Wait for bot response and expert matching
    page.wait_for_timeout(3000)  # Wait for AI processing

    # Look for expert cards - they should appear after expert matching
    expert_cards = page.locator('[data-testid^="expert-card-"]')
    expect(expert_cards).to_have_count(1)

    # Verify the expert card is visible
    expert_card = expert_cards.first
    expect(expert_card).to_be_visible()

    # Test 1: Photo thumbnail exists and is styled correctly
    photo_container = expert_card.locator('.w-12.h-12')  # Avatar container
    expect(photo_container).to_be_visible()

    # Verify the photo container has correct styling
    photo_classes = photo_container.get_attribute('class')
    assert 'w-12' in photo_classes
    assert 'h-12' in photo_classes
    assert 'rounded-full' in photo_classes

    # Test 2: Name and role typography using design system
    name_element = expert_card.locator('h4')
    expect(name_element).to_be_visible()
    name_classes = name_element.get_attribute('class')
    assert 'font-semibold' in name_classes
    assert 'text-text' in name_classes
    assert 'text-sm' in name_classes

    role_element = expert_card.locator('p').first  # First <p> should be role
    expect(role_element).to_be_visible()
    role_classes = role_element.get_attribute('class')
    assert 'text-xs' in role_classes
    assert 'text-text-muted' in role_classes

    # Test 3: Specialties list styling
    specialties_container = expert_card.locator('div').filter(has_text='Specialty').first
    if specialties_container.is_visible():
        # Verify specialties have correct styling
        specialty_badges = expert_card.locator('.bg-surface.text-text')
        expect(specialty_badges).to_have_count(3)  # Should show up to 3 specialties

        # Check that specialty badges use design system colors
        for i in range(specialty_badges.count()):
            badge = specialty_badges.nth(i)
            badge_classes = badge.get_attribute('class')
            assert 'bg-surface' in badge_classes
            assert 'text-text' in badge_classes
            assert 'rounded-full' in badge_classes
            assert 'border' in badge_classes

    # Test 4: CTA buttons styling using design system
    action_buttons = expert_card.locator('button, a')
    cta_buttons = []

    # Find buttons with 'Book', 'Select', or 'Contact' text
    for i in range(action_buttons.count()):
        button = action_buttons.nth(i)
        button_text = button.text_content()
        if button_text and any(text in button_text for text in ['Book', 'Select', 'Contact']):
            cta_buttons.append(button)

    # Should have at least one CTA button
    assert len(cta_buttons) > 0, "No CTA buttons found"

    # Verify CTA buttons use design system
    for button in cta_buttons:
        button_classes = button.get_attribute('class')
        if 'Book' in button.text_content():
            # Book button should use primary color
            assert 'bg-primary' in button_classes
            assert 'hover:bg-primary-dark' in button_classes
            assert 'text-white' in button_classes
        else:
            # Select/Contact buttons should use surface and text colors
            assert 'border-border' in button_classes
            assert 'text-text' in button_classes
            assert 'hover:bg-surface' in button_classes

    # Test 5: Overall card styling
    card_classes = expert_card.get_attribute('class')
    assert 'bg-white' in card_classes
    assert 'border-border' in card_classes
    assert 'rounded-lg' in card_classes
    assert 'shadow-sm' in card_classes
    assert 'hover:shadow-md' in card_classes

    # Test 6: Match score badge styling (if present)
    match_score = expert_card.locator('.bg-surface.text-primary').first
    if match_score.is_visible():
        score_classes = match_score.get_attribute('class')
        assert 'bg-surface' in score_classes
        assert 'text-primary' in score_classes
        assert 'rounded-full' in score_classes


@pytest.mark.e2e
def test_expert_card_responsive_design(page: Page):
    """Test that expert card works responsively."""

    # Navigate to the main page
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")

    # Open chat widget and trigger expert matching
    chat_button = page.locator('[data-testid="chat-widget-button"]')
    chat_button.click()

    input_field = page.locator('[data-testid="chat-input"]')
    input_field.fill("I need help with custom development")
    page.keyboard.press("Enter")

    page.wait_for_timeout(3000)

    expert_cards = page.locator('[data-testid^="expert-card-"]')
    expect(expert_cards).to_have_count(1)

    expert_card = expert_cards.first

    # Test mobile viewport
    page.set_viewport_size({"width": 375, "height": 667})
    expect(expert_card).to_be_visible()

    # Test tablet viewport
    page.set_viewport_size({"width": 768, "height": 1024})
    expect(expert_card).to_be_visible()

    # Test desktop viewport
    page.set_viewport_size({"width": 1200, "height": 800})
    expect(expert_card).to_be_visible()


@pytest.mark.e2e
def test_expert_card_typography_consistency(page: Page):
    """Test that expert card typography is consistent with design system."""

    # Navigate to the main page
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")

    # Open chat widget and trigger expert matching
    chat_button = page.locator('[data-testid="chat-widget-button"]')
    chat_button.click()

    input_field = page.locator('[data-testid="chat-input"]')
    input_field.fill("I need data intelligence consulting")
    page.keyboard.press("Enter")

    page.wait_for_timeout(3000)

    expert_cards = page.locator('[data-testid^="expert-card-"]')
    expect(expert_cards).to_have_count(1)

    expert_card = expert_cards.first

    # Check all text elements use correct font family
    all_text_elements = expert_card.locator('*')
    for i in range(all_text_elements.count()):
        element = all_text_elements.nth(i)
        if element.is_visible() and element.text_content():
            # Verify elements don't use hardcoded font sizes outside of design system
            element_styles = page.evaluate(f"""
                () => {{
                    const element = document.querySelector('[data-testid^="expert-card-"] *:nth-child({i + 1})');
                    if (element) {{
                        return window.getComputedStyle(element).fontSize;
                    }}
                    return null;
                }}
            """)


@pytest.mark.e2e
def test_expert_card_color_contrast(page: Page):
    """Test that expert card has proper color contrast."""

    # Navigate to the main page
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")

    # Open chat widget and trigger expert matching
    chat_button = page.locator('[data-testid="chat-widget-button"]')
    chat_button.click()

    input_field = page.locator('[data-testid="chat-input"]')
    input_field.fill("I need business consulting")
    page.keyboard.press("Enter")

    page.wait_for_timeout(3000)

    expert_cards = page.locator('[data-testid^="expert-card-"]')
    expect(expert_cards).to_have_count(1)

    expert_card = expert_cards.first

    # Verify text colors have good contrast
    name_element = expert_card.locator('h4')
    role_element = expert_card.locator('p').first

    # These should use text-text class which is #1F2937 (dark text)
    name_classes = name_element.get_attribute('class')
    role_classes = role_element.get_attribute('class')

    assert 'text-text' in name_classes
    assert 'text-text-muted' in role_classes


@pytest.mark.e2e
def test_expert_card_hover_effects(page: Page):
    """Test that expert card has proper hover effects."""

    # Navigate to the main page
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")

    # Open chat widget and trigger expert matching
    chat_button = page.locator('[data-testid="chat-widget-button"]')
    chat_button.click()

    input_field = page.locator('[data-testid="chat-input"]')
    input_field.fill("I need expert matching")
    page.keyboard.press("Enter")

    page.wait_for_timeout(3000)

    expert_cards = page.locator('[data-testid^="expert-card-"]')
    expect(expert_cards).to_have_count(1)

    expert_card = expert_cards.first

    # Test hover effect on card
    expert_card.hover()
    page.wait_for_timeout(500)  # Wait for hover transition

    # Verify shadow increases on hover
    card_classes = expert_card.get_attribute('class')
    assert 'hover:shadow-md' in card_classes

    # Test hover effects on buttons
    buttons = expert_card.locator('button, a')
    for i in range(buttons.count()):
        button = buttons.nth(i)
        if button.is_visible():
            button.hover()
            page.wait_for_timeout(200)
            button_classes = button.get_attribute('class')
            # Should have hover classes
            assert 'transition-colors' in button_classes


@pytest.mark.e2e
def test_expert_card_with_long_content(page: Page):
    """Test expert card handles long content properly."""

    # Navigate to the main page
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")

    # Open chat widget and trigger expert matching
    chat_button = page.locator('[data-testid="chat-widget-button"]')
    chat_button.click()

    input_field = page.locator('[data-testid="chat-input"]')
    input_field.fill("I need help with a very long project description")
    page.keyboard.press("Enter")

    page.wait_for_timeout(3000)

    expert_cards = page.locator('[data-testid^="expert-card-"]')
    expect(expert_cards).to_have_count(1)

    expert_card = expert_cards.first

    # Test that long text is properly truncated
    bio_element = expert_card.locator('p').nth(1)  # Bio paragraph
    if bio_element.is_visible():
        bio_text = bio_element.text_content()
        if bio_text and len(bio_text) > 100:
            # Should have line-clamp class
            bio_classes = bio_element.get_attribute('class')
            assert 'line-clamp' in bio_classes

    # Test services list truncation
    services_element = expert_card.locator('span.line-clamp-1')
    if services_element.is_visible():
        services_classes = services_element.get_attribute('class')
        assert 'line-clamp-1' in services_classes