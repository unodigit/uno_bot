import { test, expect, Page } from '@playwright/test';

/**
 * Comprehensive test for features 0-5 in the feature list
 * These tests verify the basic chat widget functionality
 */

test.beforeEach(async ({ page }) => {
  // Navigate to main page before each test
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");

  // Track console errors
  const pageErrors: any[] = [];
  page.on("console", (msg) => {
    if (msg.type === "error") {
      pageErrors.push(msg);
    }
  });
});

test.describe('Feature 0: Chat widget button renders and is visible', () => {
  test('button renders in correct position with correct size', async ({ page }) => {
    const chatButton = page.locator('[data-testid="chat-widget-button"]');

    // Verify button exists
    await expect(chatButton).toBeVisible();

    // Verify button size (60x60px)
    const box = await chatButton.boundingBox();
    expect(box).not.toBeNull();
    expect(box?.width).toBeCloseTo(60, 2);
    expect(box?.height).toBeCloseTo(60, 2);

    // Verify button position (bottom-right with 24px margin)
    // The button should be fixed positioned at bottom-6 right-6 (24px)
    const position = await chatButton.evaluate((el) => {
      const styles = window.getComputedStyle(el);
      return {
        position: styles.position,
        bottom: styles.bottom,
        right: styles.right
      };
    });

    expect(position.position).toBe('fixed');
    expect(position.bottom).toBe('24px');
    expect(position.right).toBe('24px');
  });
});

test.describe('Feature 1: Chat widget opens when clicking the button', () => {
  test('clicking button opens chat window', async ({ page }) => {
    const chatButton = page.locator('[data-testid="chat-widget-button"]');
    const chatWindow = page.locator('[data-testid="chat-window"]');

    // Initially chat window should not be visible
    await expect(chatWindow).not.toBeVisible();

    // Click the button
    await chatButton.click();

    // Wait for animation
    await page.waitForTimeout(500);

    // Chat window should now be visible
    await expect(chatWindow).toBeVisible();
  });
});

test.describe('Feature 2: Chat widget minimizes when clicking minimize button', () => {
  test('clicking minimize button minimizes the chat', async ({ page }) => {
    const chatButton = page.locator('[data-testid="chat-widget-button"]');
    const chatWindow = page.locator('[data-testid="chat-window"]');
    const minimizeButton = page.locator('[data-testid="minimize-button"]');

    // First open the chat
    await chatButton.click();
    await expect(chatWindow).toBeVisible();

    // Click minimize
    await minimizeButton.click();
    await page.waitForTimeout(500);

    // Chat window should be hidden
    await expect(chatWindow).not.toBeVisible();

    // Button should still be visible (now in minimized state)
    const minimizedButton = page.locator('[data-testid="chat-widget-button-minimized"]');
    await expect(minimizedButton).toBeVisible();
  });
});

test.describe('Feature 3: Chat session is created on first open', () => {
  test('session is created when chat opens for first time', async ({ page }) => {
    // Clear any existing session
    await page.evaluate(() => {
      localStorage.removeItem('unobot_session_id');
      localStorage.removeItem('unobot_widget_seen');
    });

    // Reload page
    await page.reload();
    await page.waitForLoadState("networkidle");

    // Open chat for the first time
    const chatButton = page.locator('[data-testid="chat-widget-button"]');
    await chatButton.click();
    await page.waitForTimeout(1000);

    // Check if session ID is stored in localStorage
    const sessionId = await page.evaluate(() => {
      return localStorage.getItem('unobot_session_id');
    });

    expect(sessionId).not.toBeNull();
    expect(sessionId?.length).toBeGreaterThan(0);

    console.log(`Session created: ${sessionId}`);
  });
});

test.describe('Feature 4: Welcome message is displayed', () => {
  test('welcome message appears when chat opens', async ({ page }) => {
    // Open chat
    const chatButton = page.locator('[data-testid="chat-widget-button"]');
    await chatButton.click();

    // Wait for messages to load
    await page.waitForTimeout(1000);

    // Check for welcome message in the chat
    const messages = page.locator('[data-testid^="message-"]');
    const messageCount = await messages.count();

    expect(messageCount).toBeGreaterThan(0);

    // Get the first message (should be welcome)
    const firstMessage = messages.first();
    await expect(firstMessage).toBeVisible();

    const messageText = await firstMessage.textContent();
    console.log(`Welcome message: ${messageText}`);

    // Verify it contains expected welcome content
    expect(messageText).toContain('Welcome');
    expect(messageText?.toLowerCase()).toContain('unobot');
  });
});

test.describe('Feature 5: User can type and send messages', () => {
  test('user can type in input and send message', async ({ page }) => {
    // Open chat
    const chatButton = page.locator('[data-testid="chat-widget-button"]');
    await chatButton.click();
    await page.waitForTimeout(1000);

    // Find input field
    const input = page.locator('input[type="text"], textarea').first();
    await expect(input).toBeVisible();

    // Type a message
    const testMessage = 'Hello, this is a test message';
    await input.fill(testMessage);

    // Verify the input has the text
    const inputValue = await input.inputValue();
    expect(inputValue).toBe(testMessage);

    // Find and click send button
    const sendButton = page.locator('[data-testid="send-button"], button[type="submit"]');
    await sendButton.click();
    await page.waitForTimeout(2000);

    // Check if user message appears in chat
    const userMessages = page.locator('[data-testid^="message-"]');
    const lastMessage = userMessages.last();
    const lastMessageText = await lastMessage.textContent();

    expect(lastMessageText).toContain(testMessage);
  });
});
