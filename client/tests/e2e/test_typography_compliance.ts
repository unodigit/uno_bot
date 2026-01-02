import { test, expect, Page } from '@playwright/test';

async function waitforElement(page: Page, selector: string, timeout = 5000) {
  await page.waitForSelector(selector, { timeout });
  return page.locator(selector);
}

async function assertStyleProperty(element: any, property: string, expected: string) {
  const actual = await element.evaluate((el: Element, prop: string) => {
    return getComputedStyle(el)[prop];
  }, property);
  expect(actual).toBe(expected);
}

test.describe('Typography Design System Compliance', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
  });

  test('should use Inter font family for all text', async ({ page }) => {
    // Wait for chat widget to load
    await waitforElement(page, '[data-testid="chat-widget"]');

    // Check that main text elements use Inter font
    const textElements = page.locator('body *:not(script):not(style)');
    const count = await textElements.count();

    for (let i = 0; i < Math.min(10, count); i++) {
      const element = textElements.nth(i);
      if (await element.isVisible()) {
        const text = await element.textContent();
        if (text && text.trim()) {
          const fontFamily = await element.evaluate((el: Element) => {
            return getComputedStyle(el).fontFamily;
          });
          expect(fontFamily).toContain('Inter');
        }
      }
    }
  });

  test('should use correct font sizes from design system', async ({ page }) => {
    // Open chat widget to see various text sizes
    const chatButton = await waitforElement(page, '[data-testid="chat-widget"]');
    await chatButton.click();

    // Wait for chat window to open
    await waitforElement(page, '[data-testid="chat-window"]');

    // Test various font sizes based on design system
    const testCases = [
      {
        selector: 'h1, h2, h3',
        expectedSize: '20px',
        description: 'Header elements should use text-xl'
      },
      {
        selector: 'p, span, div',
        expectedSize: '16px',
        description: 'Body text should use text-base'
      },
      {
        selector: '.text-sm, label, .text-xs',
        expectedSize: '14px',
        description: 'Small text should use text-sm'
      }
    ];

    for (const testCase of testCases) {
      const elements = page.locator(testCase.selector);
      const count = await elements.count();

      for (let i = 0; i < Math.min(5, count); i++) {
        const element = elements.nth(i);
        if (await element.isVisible() && await element.textContent()) {
          const fontSize = await element.evaluate((el: Element) => {
            return getComputedStyle(el).fontSize;
          });
          expect(fontSize).toBe(testCase.expectedSize);
        }
      }
    }
  });

  test('should use correct font weights from design system', async ({ page }) => {
    // Open chat widget
    const chatButton = await waitforElement(page, '[data-testid="chat-widget"]');
    await chatButton.click();

    // Wait for chat window
    await waitforElement(page, '[data-testid="chat-window"]');

    // Test font weights
    const testCases = [
      {
        selector: '.font-normal, .font-thin',
        expectedWeights: ['400', '300'],
        description: 'Normal weight should be 400'
      },
      {
        selector: '.font-medium',
        expectedWeights: ['500'],
        description: 'Medium weight should be 500'
      },
      {
        selector: '.font-semibold, .font-bold',
        expectedWeights: ['600', '700'],
        description: 'Bold weights should be 600 or 700'
      }
    ];

    for (const testCase of testCases) {
      const elements = page.locator(testCase.selector);
      const count = await elements.count();

      for (let i = 0; i < Math.min(3, count); i++) {
        const element = elements.nth(i);
        if (await element.isVisible()) {
          const fontWeight = await element.evaluate((el: Element) => {
            return getComputedStyle(el).fontWeight;
          });
          expect(testCase.expectedWeights).toContain(fontWeight);
        }
      }
    }
  });

  test('should use correct line heights from design system', async ({ page }) => {
    // Open chat widget
    const chatButton = await waitforElement(page, '[data-testid="chat-widget"]');
    await chatButton.click();

    // Wait for chat window
    await waitforElement(page, '[data-testid="chat-window"]');

    // Test line heights for different font sizes
    const testCases = [
      {
        fontSize: '16px',
        expectedLineHeight: '24px',
        description: 'Base font size should have 24px line height'
      },
      {
        fontSize: '14px',
        expectedLineHeight: '20px',
        description: 'Small font size should have 20px line height'
      },
      {
        fontSize: '20px',
        expectedLineHeight: '28px',
        description: 'Large font size should have 28px line height'
      }
    ];

    for (const testCase of testCases) {
      // Find elements with specific font size
      const elements = page.locator(`div[style*="font-size: ${testCase.fontSize}"]`);
      const count = await elements.count();

      for (let i = 0; i < Math.min(3, count); i++) {
        const element = elements.nth(i);
        if (await element.isVisible()) {
          const lineHeight = await element.evaluate((el: Element) => {
            return getComputedStyle(el).lineHeight;
          });
          expect(lineHeight).toBe(testCase.expectedLineHeight);
        }
      }
    }
  });

  test('should use design system color tokens', async ({ page }) => {
    // Open chat widget
    const chatButton = await waitforElement(page, '[data-testid="chat-widget"]');
    await chatButton.click();

    // Wait for chat window
    await waitforElement(page, '[data-testid="chat-window"]');

    // Test text color tokens
    const testCases = [
      {
        selector: '.text-text',
        expectedColor: '#1f2937', // text color from design system
        description: 'Primary text should use text-text token'
      },
      {
        selector: '.text-text-muted',
        expectedColor: '#6b7280', // text-muted color from design system
        description: 'Muted text should use text-text-muted token'
      }
    ];

    for (const testCase of testCases) {
      const elements = page.locator(testCase.selector);
      const count = await elements.count();

      for (let i = 0; i < Math.min(3, count); i++) {
        const element = elements.nth(i);
        if (await element.isVisible()) {
          const color = await element.evaluate((el: Element) => {
            return getComputedStyle(el).color;
          });

          // Convert RGB to hex for comparison
          let hexColor = color;
          if (color.startsWith('rgb')) {
            const rgb = color.replace('rgb(', '').replace(')', '').split(',');
            hexColor = `#${parseInt(rgb[0]).toString(16).padStart(2, '0')}${parseInt(rgb[1]).toString(16).padStart(2, '0')}${parseInt(rgb[2]).toString(16).padStart(2, '0')}`;
          }

          expect(hexColor.toLowerCase()).toBe(testCase.expectedColor);
        }
      }
    }
  });

  test('should maintain typography consistency across components', async ({ page }) => {
    // Open chat widget
    const chatButton = await waitforElement(page, '[data-testid="chat-widget"]');
    await chatButton.click();

    // Wait for chat window
    await waitforElement(page, '[data-testid="chat-window"]');

    // Test consistency of similar elements
    const componentsToTest = [
      {
        selector: '.text-sm',
        property: 'fontSize',
        description: 'All small text should have consistent font size'
      },
      {
        selector: '.font-semibold',
        property: 'fontWeight',
        description: 'All semi-bold text should have consistent weight'
      },
      {
        selector: '.text-text',
        property: 'color',
        description: 'All primary text should have consistent color'
      }
    ];

    for (const component of componentsToTest) {
      const elements = page.locator(component.selector);
      const count = await elements.count();
      const values: string[] = [];

      for (let i = 0; i < Math.min(5, count); i++) {
        const element = elements.nth(i);
        if (await element.isVisible()) {
          const value = await element.evaluate((el: Element, prop: string) => {
            return getComputedStyle(el)[prop];
          }, component.property);
          values.push(value);
        }
      }

      // All elements of the same class should have the same value
      const uniqueValues = new Set(values);
      expect(uniqueValues.size).toBe(1);
    }
  });

  test('should maintain responsive typography behavior', async ({ page }) => {
    // Test different viewport sizes
    const viewportSizes = [
      { width: 375, height: 812 },   // Mobile
      { width: 768, height: 1024 },  // Tablet
      { width: 1024, height: 768 },  // Desktop
      { width: 1440, height: 900 },  // Large desktop
    ];

    for (const viewport of viewportSizes) {
      await page.setViewportSize(viewport);

      // Check that typography remains readable
      const elements = page.locator('body *:not(script):not(style)');
      const count = await elements.count();

      for (let i = 0; i < Math.min(5, count); i++) {
        const element = elements.nth(i);
        if (await element.isVisible() && await element.textContent()) {
          const fontSize = await element.evaluate((el: Element) => {
            return getComputedStyle(el).fontSize;
          });

          // Font size should be reasonable (between 12px and 36px)
          const fontSizePx = parseFloat(fontSize.replace('px', ''));
          expect(fontSizePx).toBeGreaterThanOrEqual(12);
          expect(fontSizePx).toBeLessThanOrEqual(36);
        }
      }
    }
  });
});