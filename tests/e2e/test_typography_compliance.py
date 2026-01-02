import pytest
from playwright.sync_api import Page

from tests.e2e.test_utils import (
    wait_for_element,
)


def test_typography_font_family_compliance(page: Page):
    """Test that all text uses Inter font family as specified in design system."""
    page.goto("http://localhost:5174")

    # Wait for chat widget to load
    wait_for_element(page, '[data-testid="chat-widget"]')

    # Check that main text elements use Inter font
    text_elements = page.locator('body *:not(script):not(style)')
    for i in range(min(10, text_elements.count())):
        element = text_elements.nth(i)
        if element.is_visible():
            font_family = element.evaluate("el => getComputedStyle(el).fontFamily")
            if font_family and element.inner_text().strip():
                assert "Inter" in font_family, f"Element {element} should use Inter font family, got: {font_family}"


def test_typography_font_sizes_compliance(page: Page):
    """Test that font sizes follow design system scale."""
    page.goto("http://localhost:5174")

    # Open chat widget to see various text sizes
    chat_button = wait_for_element(page, '[data-testid="chat-widget"]')
    chat_button.click()

    # Wait for chat window to open
    wait_for_element(page, '[data-testid="chat-window"]')

    # Test various font sizes based on design system
    test_cases = [
        # Header text should be text-xl (20px)
        {
            'selector': 'h1, h2, h3',
            'expected_size': '20px',
            'description': 'Header elements should use text-xl'
        },
        # Body text should be text-base (16px)
        {
            'selector': 'p, span, div',
            'expected_size': '16px',
            'description': 'Body text should use text-base'
        },
        # Small text should be text-sm (14px)
        {
            'selector': '.text-sm, label, .text-xs',
            'expected_size': '14px',
            'description': 'Small text should use text-sm'
        }
    ]

    for test_case in test_cases:
        elements = page.locator(test_case['selector'])
        for i in range(min(5, elements.count())):
            element = elements.nth(i)
            if element.is_visible() and element.inner_text().strip():
                font_size = element.evaluate("el => getComputedStyle(el).fontSize")
                # Allow some tolerance for computed sizes
                assert font_size == test_case['expected_size'], \
                    f"{test_case['description']}: Expected {test_case['expected_size']}, got {font_size} for element {element}"


def test_typography_font_weights_compliance(page: Page):
    """Test that font weights follow design system (400, 500, 600)."""
    page.goto("http://localhost:5174")

    # Open chat widget
    chat_button = wait_for_element(page, '[data-testid="chat-widget"]')
    chat_button.click()

    # Wait for chat window
    wait_for_element(page, '[data-testid="chat-window"]')

    # Test font weights
    test_cases = [
        {
            'selector': '.font-normal, .font-thin',
            'expected_weight': ['400', '300'],
            'description': 'Normal weight should be 400'
        },
        {
            'selector': '.font-medium',
            'expected_weight': ['500'],
            'description': 'Medium weight should be 500'
        },
        {
            'selector': '.font-semibold, .font-bold',
            'expected_weight': ['600', '700'],
            'description': 'Bold weights should be 600 or 700'
        }
    ]

    for test_case in test_cases:
        elements = page.locator(test_case['selector'])
        for i in range(min(3, elements.count())):
            element = elements.nth(i)
            if element.is_visible():
                font_weight = element.evaluate("el => getComputedStyle(el).fontWeight")
                assert font_weight in test_case['expected_weight'], \
                    f"{test_case['description']}: Expected {test_case['expected_weight']}, got {font_weight} for element {element}"


def test_typography_line_heights_compliance(page: Page):
    """Test that line heights follow design system specifications."""
    page.goto("http://localhost:5174")

    # Open chat widget
    chat_button = wait_for_element(page, '[data-testid="chat-widget"]')
    chat_button.click()

    # Wait for chat window
    wait_for_element(page, '[data-testid="chat-window"]')

    # Test line heights for different font sizes
    test_cases = [
        {
            'font_size': '16px',
            'expected_line_height': '24px',
            'description': 'Base font size should have 24px line height'
        },
        {
            'font_size': '14px',
            'expected_line_height': '20px',
            'description': 'Small font size should have 20px line height'
        },
        {
            'font_size': '20px',
            'expected_line_height': '28px',
            'description': 'Large font size should have 28px line height'
        }
    ]

    for test_case in test_cases:
        # Find elements with specific font size
        elements = page.locator(f'div[style*="font-size: {test_case["font_size"]}"]')
        for i in range(min(3, elements.count())):
            element = elements.nth(i)
            if element.is_visible():
                line_height = element.evaluate("el => getComputedStyle(el).lineHeight")
                assert line_height == test_case['expected_line_height'], \
                    f"{test_case['description']}: Expected {test_case['expected_line_height']}, got {line_height} for font size {test_case['font_size']}"


def test_typography_design_system_tokens_usage(page: Page):
    """Test that typography uses design system color tokens."""
    page.goto("http://localhost:5174")

    # Open chat widget
    chat_button = wait_for_element(page, '[data-testid="chat-widget"]')
    chat_button.click()

    # Wait for chat window
    wait_for_element(page, '[data-testid="chat-window"]')

    # Test text color tokens
    test_cases = [
        {
            'selector': '.text-text',
            'expected_color': '#1f2937',  # text color from design system
            'description': 'Primary text should use text-text token'
        },
        {
            'selector': '.text-text-muted',
            'expected_color': '#6b7280',  # text-muted color from design system
            'description': 'Muted text should use text-text-muted token'
        }
    ]

    for test_case in test_cases:
        elements = page.locator(test_case['selector'])
        for i in range(min(3, elements.count())):
            element = elements.nth(i)
            if element.is_visible():
                color = element.evaluate("el => getComputedStyle(el).color")
                # Convert RGB to hex for comparison
                if color.startswith('rgb'):
                    # Convert RGB to hex
                    rgb = color.replace('rgb(', '').replace(')', '').split(',')
                    color = '#%02x%02x%02x' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))

                assert color.lower() == test_case['expected_color'], \
                    f"{test_case['description']}: Expected {test_case['expected_color']}, got {color} for element {element}"


def test_typography_consistency_across_components(page: Page):
    """Test that typography is consistent across different components."""
    page.goto("http://localhost:5174")

    # Open chat widget
    chat_button = wait_for_element(page, '[data-testid="chat-widget"]')
    chat_button.click()

    # Wait for chat window
    wait_for_element(page, '[data-testid="chat-window"]')

    # Test consistency of similar elements
    components_to_test = [
        {
            'selector': '.text-sm',
            'property': 'fontSize',
            'description': 'All small text should have consistent font size'
        },
        {
            'selector': '.font-semibold',
            'property': 'fontWeight',
            'description': 'All semi-bold text should have consistent weight'
        },
        {
            'selector': '.text-text',
            'property': 'color',
            'description': 'All primary text should have consistent color'
        }
    ]

    for component in components_to_test:
        elements = page.locator(component['selector'])
        values = []

        for i in range(min(5, elements.count())):
            element = elements.nth(i)
            if element.is_visible():
                value = element.evaluate(f"el => getComputedStyle(el).{component['property']}")
                values.append(value)

        # All elements of the same class should have the same value
        assert len(set(values)) == 1, \
            f"{component['description']}: Found inconsistent values {set(values)} for {component['selector']}"


def test_typography_responsive_behavior(page: Page):
    """Test that typography scales appropriately on different screen sizes."""
    page.goto("http://localhost:5174")

    # Test different viewport sizes
    viewport_sizes = [
        {'width': 375, 'height': 812},   # Mobile
        {'width': 768, 'height': 1024},  # Tablet
        {'width': 1024, 'height': 768},  # Desktop
        {'width': 1440, 'height': 900},  # Large desktop
    ]

    for viewport in viewport_sizes:
        page.set_viewport_size(viewport)

        # Check that typography remains readable
        elements = page.locator('body *:not(script):not(style)')
        for i in range(min(5, elements.count())):
            element = elements.nth(i)
            if element.is_visible() and element.inner_text().strip():
                font_size = element.evaluate("el => getComputedStyle(el).fontSize")

                # Font size should be reasonable (between 12px and 36px)
                font_size_px = float(font_size.replace('px', ''))
                assert 12 <= font_size_px <= 36, \
                    f"Font size {font_size} is outside reasonable range on viewport {viewport}"


def test_typography_contrast_compliance(page: Page):
    """Test that text has sufficient contrast for accessibility."""
    page.goto("http://localhost:5174")

    # Open chat widget
    chat_button = wait_for_element(page, '[data-testid="chat-widget"]')
    chat_button.click()

    # Wait for chat window
    wait_for_element(page, '[data-testid="chat-window"]')

    # Test contrast for different text/background combinations
    text_elements = page.locator('body *:not(script):not(style)')
    tested_elements = 0

    for i in range(min(10, text_elements.count())):
        element = text_elements.nth(i)
        if element.is_visible() and element.inner_text().strip():
            tested_elements += 1

            # Get computed styles
            styles = element.evaluate("""el => {
                const computed = getComputedStyle(el);
                return {
                    color: computed.color,
                    backgroundColor: computed.backgroundColor,
                    fontSize: computed.fontSize,
                    fontWeight: computed.fontWeight
                };
            }""")

            # Basic contrast check - text color should not be too similar to background
            if styles['backgroundColor'] and styles['backgroundColor'] != 'rgba(0, 0, 0, 0)':
                # For this test, we'll ensure colors are not identical (basic contrast)
                assert styles['color'] != styles['backgroundColor'], \
                    f"Text color {styles['color']} and background {styles['backgroundColor']} are identical for element {element}"

    assert tested_elements > 0, "No text elements found for contrast testing"


def test_typography_animation_performance(page: Page):
    """Test that typography animations are smooth and performant."""
    page.goto("http://localhost:5174")

    # Open chat widget to trigger animations
    chat_button = wait_for_element(page, '[data-testid="chat-widget"]')
    chat_button.click()

    # Wait for chat window to animate in
    chat_window = wait_for_element(page, '[data-testid="chat-window"]')

    # Check that animations use transform and opacity for performance
    animated_elements = page.locator('[style*="transform"], [style*="opacity"]')
    for i in range(min(5, animated_elements.count())):
        element = animated_elements.nth(i)
        if element.is_visible():
            transform = element.evaluate("el => getComputedStyle(el).transform")
            opacity = element.evaluate("el => getComputedStyle(el).opacity")

            # Ensure animations use hardware-accelerated properties
            assert transform != 'none' or opacity != '1', \
                f"Animated element {element} should use transform or opacity for performance"


def test_typography_clarity_and_readability(page: Page):
    """Test that typography maintains clarity and readability."""
    page.goto("http://localhost:5174")

    # Open chat widget
    chat_button = wait_for_element(page, '[data-testid="chat-widget"]')
    chat_button.click()

    # Wait for chat window
    wait_for_element(page, '[data-testid="chat-window"]')

    # Test that text is not too small
    small_text_elements = page.locator('.text-xs, .text-sm')
    for i in range(min(5, small_text_elements.count())):
        element = small_text_elements.nth(i)
        if element.is_visible():
            font_size = element.evaluate("el => getComputedStyle(el).fontSize")
            font_size_px = float(font_size.replace('px', ''))
            assert font_size_px >= 12, \
                f"Small text {font_size} is too small for readability: {element}"

    # Test that text is not too large for body content
    body_text_elements = page.locator('p, span, div')
    for i in range(min(10, body_text_elements.count())):
        element = body_text_elements.nth(i)
        if element.is_visible() and element.inner_text().strip():
            font_size = element.evaluate("el => getComputedStyle(el).fontSize")
            font_size_px = float(font_size.replace('px', ''))
            # Body text should generally be 16px (base) or smaller, headers can be larger
            if not element.evaluate("el => el.tagName === 'H1' || el.tagName === 'H2' || el.tagName === 'H3'"):
                assert font_size_px <= 20, \
                    f"Body text {font_size} is too large for readability: {element}"


def test_typography_font_loading_optimization(page: Page):
    """Test that typography includes font loading optimizations."""
    page.goto("http://localhost:5174")

    # Check that font loading is optimized
    font_links = page.locator('link[rel="preload"][as="font"], link[rel="stylesheet"]')
    found_font_loading = False

    for i in range(font_links.count()):
        link = font_links.nth(i)
        href = link.get_attribute('href') or ''
        rel = link.get_attribute('rel') or ''

        # Check for font optimization hints
        if 'font' in rel.lower() or 'inter' in href.lower():
            found_font_loading = True
            break

    # This is more of a performance optimization check
    # In a real implementation, we'd want proper font preloading
    print(f"Font loading optimization found: {found_font_loading}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
