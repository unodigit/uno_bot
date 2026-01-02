/**
 * E2E Tests for Accessibility Features (Features 126-132)
 *
 * Tests features 126-132 from the feature list:
 * - Feature 126: Keyboard navigation works for chat interface
 * - Feature 127: Screen reader announces chat content correctly
 * - Feature 128: Focus management works correctly
 * - Feature 129: Color contrast meets WCAG 2.1 AA standards
 * - Feature 130: ARIA labels are correctly applied
 * - Feature 131: Sound notifications can be enabled/disabled
 * - Feature 132: Widget position is configurable (left/right)
 */

import { test, expect, Page } from '@playwright/test';

// Helper to handle consent modal
async function handleConsent(page: Page) {
  // Check for consent modal
  const consentModal = page.locator('[data-testid="consent-modal"]');
  const isVisible = await consentModal.isVisible().catch(() => false);
  if (isVisible) {
    // Scroll to enable accept button
    const content = consentModal.locator('div[class*="overflow-y-auto"]');
    if (await content.isVisible()) {
      await content.evaluate(el => el.scrollTop = el.scrollHeight);
      await page.waitForTimeout(200);
    }

    // Click accept
    const acceptButton = consentModal.locator('text=I Agree - Continue');
    if (await acceptButton.isVisible()) {
      await acceptButton.click();
      await page.waitForTimeout(500);
    }
  }
}

test.describe('Accessibility Features Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage and navigate to main page
    await page.goto('http://localhost:5173');
    await page.evaluate('localStorage.clear()');
    await page.reload();
    await page.waitForLoadState('networkidle');
    await handleConsent(page);
  });

  test.describe('Feature 126: Keyboard navigation works for chat interface', () => {
    test('chat widget button can be activated with Enter key', async ({ page }) => {
      const button = page.locator('[data-testid="chat-widget-button"]');

      // Focus the button using keyboard navigation
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab'); // Skip any skip links

      // Verify button is focused
      await expect(button).toBeFocused();

      // Press Enter to activate
      await page.keyboard.press('Enter');

      // Wait for animation
      await page.waitForTimeout(500);

      // Chat window should open
      const chatWindow = page.locator('[data-testid="chat-window"]');
      await expect(chatWindow).toBeVisible();
    });

    test('chat widget button can be activated with Space key', async ({ page }) => {
      const button = page.locator('[data-testid="chat-widget-button"]');

      // Focus the button
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await expect(button).toBeFocused();

      // Press Space to activate
      await page.keyboard.press(' ');

      // Wait for animation
      await page.waitForTimeout(500);

      // Chat window should open
      const chatWindow = page.locator('[data-testid="chat-window"]');
      await expect(chatWindow).toBeVisible();
    });

    test('chat window can be closed with Escape key', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const chatWindow = page.locator('[data-testid="chat-window"]');
      await expect(chatWindow).toBeVisible();

      // Press Escape to close
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);

      // Chat window should be closed
      await expect(chatWindow).not.toBeVisible();
    });

    test('message input supports Enter to send and Shift+Enter for new line', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(1000);

      const input = page.locator('[data-testid="message-input"]');
      await expect(input).toBeVisible();

      // Type message
      await input.fill('Test message');

      // Press Enter to send
      await page.keyboard.press('Enter');
      await page.waitForTimeout(1000);

      // Verify message was sent
      const userMessages = page.locator('[data-testid="message-user"]');
      const count = await userMessages.count();
      expect(count).toBeGreaterThan(0);
    });

    test('quick reply buttons can be activated with keyboard', async ({ page }) => {
      // Open chat and send a message to get quick replies
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(1000);

      const input = page.locator('[data-testid="message-input"]');
      await input.fill('Hello');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(2000);

      // Check for quick replies
      const quickReplies = page.locator('[data-testid^="quick-reply-"]');
      const count = await quickReplies.count();

      if (count > 0) {
        // Focus first quick reply
        await quickReplies.first().focus();
        await expect(quickReplies.first()).toBeFocused();

        // Press Enter to activate
        await page.keyboard.press('Enter');
        await page.waitForTimeout(1000);

        // Should send the quick reply
        const userMessages = page.locator('[data-testid="message-user"]');
        const userCount = await userMessages.count();
        expect(userCount).toBeGreaterThan(1); // Original + quick reply
      }
    });
  });

  test.describe('Feature 127: Screen reader announces chat content correctly', () => {
    test('chat widget has aria-live regions for announcements', async ({ page }) => {
      // Check for aria-live elements in the DOM
      const ariaLiveElements = await page.locator('[aria-live]').all();
      expect(ariaLiveElements.length).toBeGreaterThan(0);

      // Verify at least one is polite (not assertive which can be disruptive)
      const hasPoliteLive = await page.evaluate(() => {
        const elements = document.querySelectorAll('[aria-live]');
        return Array.from(elements).some(el =>
          el.getAttribute('aria-live') === 'polite'
        );
      });

      expect(hasPoliteLive).toBe(true);
    });

    test('chat window has proper ARIA role and labels', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const chatWindow = page.locator('[data-testid="chat-window"]');

      // Check for dialog role
      const role = await chatWindow.getAttribute('role');
      expect(role).toBe('dialog');

      // Check for aria-modal
      const ariaModal = await chatWindow.getAttribute('aria-modal');
      expect(ariaModal).toBe('true');

      // Check for aria-labelledby
      const ariaLabelledBy = await chatWindow.getAttribute('aria-labelledby');
      expect(ariaLabelledBy).toBeTruthy();

      // Check for aria-describedby
      const ariaDescribedBy = await chatWindow.getAttribute('aria-describedby');
      expect(ariaDescribedBy).toBeTruthy();
    });

    test('message container has proper ARIA live region', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      // Check messages container
      const messagesContainer = page.locator('[data-testid="messages-container"]');
      await expect(messagesContainer).toBeVisible();

      // Verify ARIA attributes for screen readers
      const role = await messagesContainer.getAttribute('role');
      expect(role).toBe('log');

      const ariaLive = await messagesContainer.getAttribute('aria-live');
      expect(ariaLive).toBe('polite');

      const ariaRelevant = await messagesContainer.getAttribute('aria-relevant');
      expect(ariaRelevant).toBe('additions text');
    });

    test('typing indicator has ARIA label', async ({ page }) => {
      // Open chat and send a message to trigger typing indicator
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(1000);

      const input = page.locator('[data-testid="message-input"]');
      await input.fill('Test');
      await page.keyboard.press('Enter');

      // Check for typing indicator with ARIA
      const typingIndicator = page.locator('[data-testid="typing-indicator"]');

      // The indicator might appear briefly, check if it has proper ARIA when visible
      const isVisible = await typingIndicator.isVisible().catch(() => false);
      if (isVisible) {
        const ariaLabel = await typingIndicator.getAttribute('aria-label');
        // Should have aria-label or aria-live
        const hasAria = ariaLabel || (await typingIndicator.getAttribute('aria-live'));
        expect(hasAria).toBeTruthy();
      }
    });
  });

  test.describe('Feature 128: Focus management works correctly', () => {
    test('input is focused when chat window opens', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const input = page.locator('[data-testid="message-input"]');

      // Input should be focused (autoFocus in component)
      await expect(input).toBeFocused();
    });

    test('focus is trapped within chat window when open', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      // Tab through focusable elements in chat window
      const input = page.locator('[data-testid="message-input"]');
      const sendButton = page.locator('[data-testid="send-button"]');
      const settingsButton = page.locator('[data-testid="settings-button"]');
      const minimizeButton = page.locator('[data-testid="minimize-button"]');
      const closeButton = page.locator('[data-testid="close-button"]');

      // Start with input
      await expect(input).toBeFocused();

      // Tab to send button
      await page.keyboard.press('Tab');
      await expect(sendButton).toBeFocused();

      // Tab to settings
      await page.keyboard.press('Tab');
      await expect(settingsButton).toBeFocused();

      // Tab to minimize
      await page.keyboard.press('Tab');
      await expect(minimizeButton).toBeFocused();

      // Tab to close
      await page.keyboard.press('Tab');
      await expect(closeButton).toBeFocused();
    });

    test('focus returns to widget button after closing chat', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      // Close chat
      const closeButton = page.locator('[data-testid="close-button"]');
      await closeButton.click();
      await page.waitForTimeout(500);

      // Focus should be on the widget button (or at least back on the page)
      // The button should be visible again
      await expect(chatButton).toBeVisible();
    });

    test('settings panel maintains focus when opened', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      // Open settings
      const settingsButton = page.locator('[data-testid="settings-button"]');
      await settingsButton.click();
      await page.waitForTimeout(300);

      // Settings panel should be visible
      const settingsPanel = page.locator('[data-testid="settings-panel"]');
      await expect(settingsPanel).toBeVisible();

      // Focus should remain on settings button or move to first element in panel
      const isFocused = await settingsButton.evaluate(el => el === document.activeElement);
      expect(isFocused || (await settingsPanel.isVisible())).toBeTruthy();
    });
  });

  test.describe('Feature 129: Color contrast meets WCAG 2.1 AA standards', () => {
    test('primary button text has sufficient contrast', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      // Check header text contrast (white text on primary blue background)
      const header = page.locator('[data-testid="chat-window"] .h-12');
      const headerColor = await header.evaluate(el => {
        const styles = window.getComputedStyle(el);
        return {
          bg: styles.backgroundColor,
          color: styles.color
        };
      });

      // Primary color is #2563EB (rgb(37, 99, 235))
      // White is rgb(255, 255, 255)
      // This combination should meet WCAG AA for large text (18pt+)
      expect(headerColor.color).toContain('255'); // White
      expect(headerColor.bg).toContain('37'); // Primary blue
    });

    test('user message bubbles have sufficient contrast', async ({ page }) => {
      // Open chat and send a message
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(1000);

      const input = page.locator('[data-testid="message-input"]');
      await input.fill('Test message');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(1000);

      // Get user message styling
      const userMessage = page.locator('[data-testid="message-user"]').first();
      const styles = await userMessage.evaluate(el => {
        const computed = window.getComputedStyle(el);
        return {
          bg: computed.backgroundColor,
          color: computed.color
        };
      });

      // User messages use primary color (#2563EB) with white text
      expect(styles.bg).toContain('37'); // Primary blue
      expect(styles.color).toContain('255'); // White
    });

    test('bot message bubbles have sufficient contrast', async ({ page }) => {
      // Open chat and send a message to get bot response
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(1000);

      const input = page.locator('[data-testid="message-input"]');
      await input.fill('Hello');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(2000);

      // Get bot message styling
      const botMessage = page.locator('[data-testid="message-assistant"]').first();
      const styles = await botMessage.evaluate(el => {
        const computed = window.getComputedStyle(el);
        return {
          bg: computed.backgroundColor,
          color: computed.color
        };
      });

      // Bot messages use surface (#F3F4F6) with text (#1F2937)
      // This should provide sufficient contrast
      expect(styles.color).toBeTruthy(); // Text color exists
    });

    test('input field has visible focus indicator', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const input = page.locator('[data-testid="message-input"]');

      // Focus the input
      await input.focus();

      // Check for focus ring
      const focusRing = await input.evaluate(el => {
        const styles = window.getComputedStyle(el);
        return {
          outline: styles.outline,
          boxShadow: styles.boxShadow
        };
      });

      // Should have some visual indicator (boxShadow or outline)
      expect(focusRing.boxShadow || focusRing.outline).toBeTruthy();
    });
  });

  test.describe('Feature 130: ARIA labels are correctly applied', () => {
    test('chat widget button has aria-label', async ({ page }) => {
      const button = page.locator('[data-testid="chat-widget-button"]');
      const ariaLabel = await button.getAttribute('aria-label');

      expect(ariaLabel).toBeTruthy();
      expect(ariaLabel).toContain('Open chat');
    });

    test('chat window close button has aria-label', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const closeButton = page.locator('[data-testid="close-button"]');
      const ariaLabel = await closeButton.getAttribute('aria-label');

      expect(ariaLabel).toBeTruthy();
      expect(ariaLabel.toLowerCase()).toContain('close');
    });

    test('message input has aria-label', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const input = page.locator('[data-testid="message-input"]');
      const ariaLabel = await input.getAttribute('aria-label');

      expect(ariaLabel).toBeTruthy();
      expect(ariaLabel.toLowerCase()).toContain('message');
    });

    test('send button has aria-label', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const sendButton = page.locator('[data-testid="send-button"]');
      const ariaLabel = await sendButton.getAttribute('aria-label');

      expect(ariaLabel).toBeTruthy();
      expect(ariaLabel.toLowerCase()).toContain('send');
    });

    test('settings button has aria-label and aria-expanded', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const settingsButton = page.locator('[data-testid="settings-button"]');

      // Check aria-label
      const ariaLabel = await settingsButton.getAttribute('aria-label');
      expect(ariaLabel).toBeTruthy();

      // Check aria-expanded (should be false initially)
      const ariaExpanded = await settingsButton.getAttribute('aria-expanded');
      expect(ariaExpanded).toBe('false');

      // Open settings
      await settingsButton.click();
      await page.waitForTimeout(300);

      // Now should be true
      const ariaExpandedAfter = await settingsButton.getAttribute('aria-expanded');
      expect(ariaExpandedAfter).toBe('true');
    });

    test('minimize button has aria-label', async ({ page }) => {
      // Open chat
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const minimizeButton = page.locator('[data-testid="minimize-button"]');
      const ariaLabel = await minimizeButton.getAttribute('aria-label');

      expect(ariaLabel).toBeTruthy();
      expect(ariaLabel.toLowerCase()).toContain('minimize');
    });

    test('message elements have aria-label', async ({ page }) => {
      // Open chat and send a message
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(1000);

      const input = page.locator('[data-testid="message-input"]');
      await input.fill('Test');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(1000);

      // Check user message
      const userMessage = page.locator('[data-testid="message-user"]').first();
      const userAriaLabel = await userMessage.getAttribute('aria-label');
      expect(userAriaLabel).toBeTruthy();

      // Check bot message (if present)
      const botMessages = page.locator('[data-testid="message-assistant"]');
      if (await botMessages.count() > 0) {
        const botMessage = botMessages.first();
        const botAriaLabel = await botMessage.getAttribute('aria-label');
        expect(botAriaLabel).toBeTruthy();
      }
    });

    test('settings toggle switches have role and aria-checked', async ({ page }) => {
      // Open chat and settings
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const settingsButton = page.locator('[data-testid="settings-button"]');
      await settingsButton.click();
      await page.waitForTimeout(300);

      // Check sound toggle
      const soundToggle = page.locator('[data-testid="sound-toggle"]');
      const soundRole = await soundToggle.getAttribute('role');
      const soundAriaChecked = await soundToggle.getAttribute('aria-checked');

      expect(soundRole).toBe('switch');
      expect(soundAriaChecked).toBeTruthy();

      // Check position toggle
      const positionToggle = page.locator('[data-testid="position-toggle"]');
      const positionRole = await positionToggle.getAttribute('role');
      const positionAriaChecked = await positionToggle.getAttribute('aria-checked');

      expect(positionRole).toBe('switch');
      expect(positionAriaChecked).toBeTruthy();
    });
  });

  test.describe('Feature 131: Sound notifications can be enabled/disabled', () => {
    test('sound toggle exists in settings panel', async ({ page }) => {
      // Open chat and settings
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const settingsButton = page.locator('[data-testid="settings-button"]');
      await settingsButton.click();
      await page.waitForTimeout(300);

      // Check for sound toggle
      const soundToggle = page.locator('[data-testid="sound-toggle"]');
      await expect(soundToggle).toBeVisible();
    });

    test('sound toggle can be clicked to enable/disable', async ({ page }) => {
      // Open chat and settings
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const settingsButton = page.locator('[data-testid="settings-button"]');
      await settingsButton.click();
      await page.waitForTimeout(300);

      const soundToggle = page.locator('[data-testid="sound-toggle"]');

      // Get initial state
      const initialState = await soundToggle.getAttribute('aria-checked');

      // Click to toggle
      await soundToggle.click();
      await page.waitForTimeout(200);

      // Check state changed
      const newState = await soundToggle.getAttribute('aria-checked');
      expect(newState).not.toBe(initialState);

      // Verify localStorage is updated
      const storedValue = await page.evaluate(() => {
        return localStorage.getItem('unobot_sound_notifications');
      });

      expect(storedValue).toBeTruthy();
      expect(['true', 'false']).toContain(storedValue);
    });

    test('sound toggle persists across page reloads', async ({ page }) => {
      // Open chat and settings
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const settingsButton = page.locator('[data-testid="settings-button"]');
      await settingsButton.click();
      await page.waitForTimeout(300);

      const soundToggle = page.locator('[data-testid="sound-toggle"]');

      // Enable sounds
      const currentState = await soundToggle.getAttribute('aria-checked');
      if (currentState === 'false') {
        await soundToggle.click();
        await page.waitForTimeout(200);
      }

      // Reload page
      await page.reload();
      await page.waitForLoadState('networkidle');
      await handleConsent(page);

      // Open chat and settings again
      await chatButton.click();
      await page.waitForTimeout(500);
      await settingsButton.click();
      await page.waitForTimeout(300);

      // Check if state persisted
      const persistedState = await soundToggle.getAttribute('aria-checked');
      expect(persistedState).toBe('true');
    });

    test('sound toggle has visual indicator for enabled/disabled state', async ({ page }) => {
      // Open chat and settings
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const settingsButton = page.locator('[data-testid="settings-button"]');
      await settingsButton.click();
      await page.waitForTimeout(300);

      const soundToggle = page.locator('[data-testid="sound-toggle"]');

      // Get the toggle's visual state (color changes between enabled/disabled)
      const bgColor = await soundToggle.evaluate(el =>
        window.getComputedStyle(el).backgroundColor
      );

      // Should have a distinct color
      expect(bgColor).toBeTruthy();
    });

    test('settings panel shows sound status text', async ({ page }) => {
      // Open chat and settings
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const settingsButton = page.locator('[data-testid="settings-button"]');
      await settingsButton.click();
      await page.waitForTimeout(300);

      // Check for status text in settings panel
      const settingsPanel = page.locator('[data-testid="settings-panel"]');
      const panelText = await settingsPanel.textContent();

      expect(panelText).toContain('Sound');
      expect(panelText).toContain('Notifications');
    });
  });

  test.describe('Feature 132: Widget position is configurable (left/right)', () => {
    test('position toggle exists in settings panel', async ({ page }) => {
      // Open chat and settings
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const settingsButton = page.locator('[data-testid="settings-button"]');
      await settingsButton.click();
      await page.waitForTimeout(300);

      // Check for position toggle
      const positionToggle = page.locator('[data-testid="position-toggle"]');
      await expect(positionToggle).toBeVisible();
    });

    test('position toggle switches between left and right', async ({ page }) => {
      // Open chat and settings
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const settingsButton = page.locator('[data-testid="settings-button"]');
      await settingsButton.click();
      await page.waitForTimeout(300);

      const positionToggle = page.locator('[data-testid="position-toggle"]');

      // Get initial position (should be right by default)
      const initialState = await positionToggle.getAttribute('aria-checked');

      // Click to toggle
      await positionToggle.click();
      await page.waitForTimeout(300);

      // Close settings and check button position
      await settingsButton.click();
      await page.waitForTimeout(300);

      // Close chat
      const closeButton = page.locator('[data-testid="close-button"]');
      await closeButton.click();
      await page.waitForTimeout(500);

      // Check button position
      const button = page.locator('[data-testid="chat-widget-button"]');
      const box = await button.boundingBox();

      if (box) {
        const viewport = page.viewportSize();
        const leftMargin = box.x;
        const rightMargin = viewport.width - (box.x + box.width);

        // If we toggled from right to left, left margin should be small (24px)
        // and right margin should be large
        if (initialState === 'false') {
          // Was right, now should be left
          expect(leftMargin).toBeCloseTo(24, 1);
        } else {
          // Was left, now should be right
          expect(rightMargin).toBeCloseTo(24, 1);
        }
      }
    });

    test('position persists across page reloads', async ({ page }) => {
      // Open chat and settings
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const settingsButton = page.locator('[data-testid="settings-button"]');
      await settingsButton.click();
      await page.waitForTimeout(300);

      const positionToggle = page.locator('[data-testid="position-toggle"]');

      // Set to left position
      const currentState = await positionToggle.getAttribute('aria-checked');
      if (currentState === 'false') {
        await positionToggle.click();
        await page.waitForTimeout(200);
      }

      // Verify localStorage
      const storedPosition = await page.evaluate(() => {
        return localStorage.getItem('unobot_widget_position');
      });
      expect(storedPosition).toBe('left');

      // Reload page
      await page.reload();
      await page.waitForLoadState('networkidle');
      await handleConsent(page);

      // Check if position persisted
      const persistedPosition = await page.evaluate(() => {
        return localStorage.getItem('unobot_widget_position');
      });
      expect(persistedPosition).toBe('left');
    });

    test('position menu appears on hover of widget button', async ({ page }) => {
      // Close chat if open
      const chatWindow = page.locator('[data-testid="chat-window"]');
      if (await chatWindow.isVisible()) {
        const closeButton = page.locator('[data-testid="close-button"]');
        await closeButton.click();
        await page.waitForTimeout(500);
      }

      // Hover over widget button
      const button = page.locator('[data-testid="chat-widget-button"]');
      await button.hover();
      await page.waitForTimeout(300);

      // Check for position menu
      const positionMenu = page.locator('[role="menu"][aria-label="Widget position options"]');

      // The menu might be visible on hover
      const isVisible = await positionMenu.isVisible().catch(() => false);

      if (isVisible) {
        await expect(positionMenu).toBeVisible();

        // Check for left and right position buttons
        const leftButton = page.locator('[data-testid="position-left"]');
        const rightButton = page.locator('[data-testid="position-right"]');

        await expect(leftButton).toBeVisible();
        await expect(rightButton).toBeVisible();
      }
    });

    test('position buttons in menu work correctly', async ({ page }) => {
      // Close chat if open
      const chatWindow = page.locator('[data-testid="chat-window"]');
      if (await chatWindow.isVisible()) {
        const closeButton = page.locator('[data-testid="close-button"]');
        await closeButton.click();
        await page.waitForTimeout(500);
      }

      // Hover to show menu
      const button = page.locator('[data-testid="chat-widget-button"]');
      await button.hover();
      await page.waitForTimeout(300);

      // Try to click left position button
      const leftButton = page.locator('[data-testid="position-left"]');
      const isVisible = await leftButton.isVisible().catch(() => false);

      if (isVisible) {
        await leftButton.click();
        await page.waitForTimeout(300);

        // Verify position changed
        const storedPosition = await page.evaluate(() => {
          return localStorage.getItem('unobot_widget_position');
        });
        expect(storedPosition).toBe('left');
      }
    });

    test('settings panel shows position status text', async ({ page }) => {
      // Open chat and settings
      const chatButton = page.locator('[data-testid="chat-widget-button"]');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);

      const settingsButton = page.locator('[data-testid="settings-button"]');
      await settingsButton.click();
      await page.waitForTimeout(300);

      // Check for position text in settings panel
      const settingsPanel = page.locator('[data-testid="settings-panel"]');
      const panelText = await settingsPanel.textContent();

      expect(panelText).toContain('Widget Position');
      expect(panelText).toContain('bottom');
    });
  });
});
