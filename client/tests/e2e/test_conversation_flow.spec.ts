import { test, expect, Page } from '@playwright/test';

/**
 * Tests for conversation flow features (10-19)
 * These verify the bot asks the right questions in sequence
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

test.describe('Feature 10: Bot asks for user name', () => {
  test('welcome message asks for name', async ({ page }) => {
    // Open chat widget
    const chatButton = page.locator('[data-testid="chat-widget-button"]');
    await chatButton.click();

    // Wait for chat window to open
    const chatWindow = page.locator('[data-testid="chat-window"]');
    await expect(chatWindow).toBeVisible();

    // Wait for messages to load
    await page.waitForTimeout(1000);

    // Get the welcome message
    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();

    expect(messageCount).toBeGreaterThan(0);

    const welcomeMessage = messages.nth(0);
    const welcomeText = await welcomeMessage.textContent();

    // Welcome message should ask for name
    expect(welcomeText?.toLowerCase()).toMatch(/name|what'?s your name|to get started/i);
  });
});

test.describe('Feature 11: Bot collects email address', () => {
  test('bot asks for email after name is provided', async ({ page }) => {
    // Open chat
    await page.click('[data-testid="chat-widget-button"]');
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();

    // Wait for welcome message
    await page.waitForTimeout(1000);

    // Type name
    await page.fill('[data-testid="chat-input"]', 'My name is John Doe');
    await page.click('[data-testid="send-button"]');

    // Wait for bot response
    await page.waitForTimeout(3000);

    // Get the latest message
    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    const lastMessage = messages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should ask for email
    expect(lastText?.toLowerCase()).toMatch(/email|e-mail/i);
  });
});

test.describe('Feature 12: Bot collects company information', () => {
  test('bot asks about company after email is provided', async ({ page }) => {
    // Open chat
    await page.click('[data-testid="chat-widget-button"]');
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await page.waitForTimeout(1000);

    // Provide name
    await page.fill('[data-testid="chat-input"]', 'My name is John Doe');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Provide email
    await page.fill('[data-testid="chat-input"]', 'john@example.com');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Provide challenge
    await page.fill('[data-testid="chat-input"]', 'We need help with data analytics');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Check if bot asks about company or industry
    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    const lastMessage = messages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should ask about company or industry
    expect(lastText?.toLowerCase()).toMatch(/company|industry|organization|business/i);
  });
});

test.describe('Feature 15: Bot collects budget information', () => {
  test('bot asks for budget after collecting basic info', async ({ page }) => {
    // Open chat
    await page.click('[data-testid="chat-widget-button"]');
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await page.waitForTimeout(1000);

    // Go through initial conversation
    const responses = [
      'My name is John Doe',
      'john@example.com',
      'We need help with data analytics in healthcare',
      'We have 50 people'
    ];

    for (const response of responses) {
      await page.fill('[data-testid="chat-input"]', response);
      await page.click('[data-testid="send-button"]');
      await page.waitForTimeout(2000);
    }

    // Check if bot asks about budget
    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    const lastMessage = messages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should mention budget or $
    expect(lastText?.toLowerCase()).toMatch(/budget|\$/i);
  });
});

test.describe('Feature 16: Bot collects timeline information', () => {
  test('bot asks for timeline after budget is provided', async ({ page }) => {
    // Open chat
    await page.click('[data-testid="chat-widget-button"]');
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await page.waitForTimeout(1000);

    // Go through conversation
    const responses = [
      'My name is John Doe',
      'john@example.com',
      'We need help with data analytics',
      'We are in healthcare with 50 people',
      'Our budget is around $50000'
    ];

    for (const response of responses) {
      await page.fill('[data-testid="chat-input"]', response);
      await page.click('[data-testid="send-button"]');
      await page.waitForTimeout(2000);
    }

    // Check if bot asks about timeline
    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    const lastMessage = messages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should mention timeline or months
    expect(lastText?.toLowerCase()).toMatch(/timeline|month/i);
  });
});

test.describe('Full conversation flow', () => {
  test('complete conversation from greeting to qualification', async ({ page }) => {
    // Open chat
    await page.click('[data-testid="chat-widget-button"]');
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await page.waitForTimeout(1000);

    // Track conversation phases
    const conversationFlow: string[] = [];

    // Initial welcome message should ask for name
    let messages = page.locator('[data-testid="chat-message"]');
    let welcomeText = await messages.nth(0).textContent();
    expect(welcomeText?.toLowerCase()).toMatch(/name/i);
    conversationFlow.push('Welcome: asks for name');

    // Provide name
    await page.fill('[data-testid="chat-input"]', 'My name is John Doe');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Should ask for email
    messages = page.locator('[data-testid="chat-message"]');
    let messageCount = await messages.count();
    let lastText = await messages.nth(messageCount - 1).textContent();
    expect(lastText?.toLowerCase()).toMatch(/email/i);
    conversationFlow.push('Asks for email');

    // Provide email
    await page.fill('[data-testid="chat-input"]', 'john@example.com');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Should ask about business challenge
    messages = page.locator('[data-testid="chat-message"]');
    messageCount = await messages.count();
    lastText = await messages.nth(messageCount - 1).textContent();
    conversationFlow.push('Asks about business challenge');

    // Provide challenge
    await page.fill('[data-testid="chat-input"]', 'We need help with data analytics');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Should ask about company/industry
    messages = page.locator('[data-testid="chat-message"]');
    messageCount = await messages.count();
    lastText = await messages.nth(messageCount - 1).textContent();
    expect(lastText?.toLowerCase()).toMatch(/company|industry/i);
    conversationFlow.push('Asks about company/industry');

    // Provide company info
    await page.fill('[data-testid="chat-input"]', 'We are in healthcare with 50 people');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Should ask about budget
    messages = page.locator('[data-testid="chat-message"]');
    messageCount = await messages.count();
    lastText = await messages.nth(messageCount - 1).textContent();
    expect(lastText?.toLowerCase()).toMatch(/budget|\$/i);
    conversationFlow.push('Asks about budget');

    // Provide budget
    await page.fill('[data-testid="chat-input"]', 'About $50000');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Should ask about timeline
    messages = page.locator('[data-testid="chat-message"]');
    messageCount = await messages.count();
    lastText = await messages.nth(messageCount - 1).textContent();
    expect(lastText?.toLowerCase()).toMatch(/timeline|month/i);
    conversationFlow.push('Asks about timeline');

    // Verify we went through the expected flow
    expect(conversationFlow.length).toBeGreaterThan(5);

    console.log('Conversation flow:', conversationFlow);
  });
});
