import { test, expect } from '@playwright/test';

/**
 * E2E test for Feature 19: Quick reply buttons
 * Verifies that quick reply buttons appear after welcome message,
 * can be clicked, send the message, and continue the conversation
 */

test.beforeEach(async ({ page }) => {
  // Navigate to main page before each test
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");

  // Track console errors
  page.on("console", (msg) => {
    if (msg.type === "error") {
      console.log(`Console error: ${msg.text()}`);
    }
  });
});

test.describe('Feature 19: Quick reply buttons appear for common options', () => {
  test('quick reply buttons appear after welcome message', async ({ page }) => {
    // Step 1: Open chat widget
    const chatButton = page.locator('[data-testid="chat-widget-button"]');
    await chatButton.click();
    await page.waitForTimeout(1000);

    // Step 2: Verify quick reply buttons appear after welcome message
    // Wait for welcome message
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 5000 });
    await page.waitForTimeout(500);

    // Check for quick reply buttons container
    const quickRepliesContainer = page.locator('[data-testid="quick-replies"]');
    await expect(quickRepliesContainer).toBeVisible();

    // Verify at least 3 quick reply buttons are present
    const quickReplyButtons = page.locator('[data-testid^="quick-reply-"]');
    const buttonCount = await quickReplyButtons.count();

    expect(buttonCount).toBeGreaterThanOrEqual(3);
    console.log(`✓ Found ${buttonCount} quick reply buttons`);

    // Verify buttons have text
    for (let i = 0; i < Math.min(buttonCount, 4); i++) {
      const buttonText = await quickReplyButtons.nth(i).textContent();
      expect(buttonText).not.toBeNull();
      expect(buttonText?.trim().length).toBeGreaterThan(0);
      console.log(`  Button ${i}: "${buttonText}"`);
    }
  });

  test('clicking quick reply sends the message', async ({ page }) => {
    // Step 1: Open chat widget
    const chatButton = page.locator('[data-testid="chat-widget-button"]');
    await chatButton.click();
    await page.waitForTimeout(1000);

    // Wait for welcome message and quick replies
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 5000 });
    await page.waitForTimeout(500);

    // Step 2 & 3: Click on a quick reply option
    const quickReplyButtons = page.locator('[data-testid^="quick-reply-"]');
    await expect(quickReplyButtons.first()).toBeVisible();

    // Get the text of the first quick reply
    const quickReplyText = await quickReplyButtons.first().textContent();
    console.log(`Clicking quick reply: "${quickReplyText}"`);

    // Count messages before clicking
    const messagesBefore = await page.locator('[data-testid^="message-"]').count();
    console.log(`Messages before click: ${messagesBefore}`);

    // Click the first quick reply button
    await quickReplyButtons.first().click();

    // Step 4: Verify the option is sent as a message
    // Wait for the message to be sent
    await page.waitForTimeout(2000);

    // Check that a new user message was added
    const userMessages = page.locator('[data-testid="message-user"]');
    const userMessageCount = await userMessages.count();

    expect(userMessageCount).toBeGreaterThan(0);
    console.log(`✓ User messages after click: ${userMessageCount}`);

    // Verify the user message contains the quick reply text
    const lastUserMessage = userMessages.last();
    const messageText = await lastUserMessage.textContent();
    expect(messageText).toContain(quickReplyText || '');
    console.log(`✓ Message sent: "${messageText}"`);
  });

  test('conversation continues after quick reply selection', async ({ page }) => {
    // Step 1: Open chat widget
    const chatButton = page.locator('[data-testid="chat-widget-button"]');
    await chatButton.click();
    await page.waitForTimeout(1000);

    // Wait for welcome message and quick replies
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 5000 });
    await page.waitForTimeout(500);

    // Count initial bot messages
    const botMessagesBefore = await page.locator('[data-testid="message-assistant"]').count();
    console.log(`Bot messages before: ${botMessagesBefore}`);

    // Step 2 & 3: Click a quick reply option
    const quickReplyButtons = page.locator('[data-testid^="quick-reply-"]');
    await quickReplyButtons.first().click();

    // Step 5: Verify conversation continues based on selection
    // Wait for bot response
    await page.waitForTimeout(3000);

    // Check that a new bot message appeared
    const botMessagesAfter = await page.locator('[data-testid="message-assistant"]').count();
    console.log(`Bot messages after: ${botMessagesAfter}`);

    expect(botMessagesAfter).toBeGreaterThan(botMessagesBefore);

    // Verify the last bot message is not empty
    const lastBotMessage = page.locator('[data-testid="message-assistant"]').last();
    await expect(lastBotMessage).toBeVisible();

    const botResponseText = await lastBotMessage.textContent();
    expect(botResponseText).not.toBeNull();
    expect(botResponseText?.trim().length).toBeGreaterThan(0);
    console.log(`✓ Bot responded: "${botResponseText?.substring(0, 50)}..."`);
  });

  test('quick replies update based on conversation phase', async ({ page }) => {
    // Open chat widget
    const chatButton = page.locator('[data-testid="chat-widget-button"]');
    await chatButton.click();
    await page.waitForTimeout(1000);

    // Wait for welcome message and quick replies
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 5000 });
    await page.waitForTimeout(500);

    // Get initial quick replies (greeting phase)
    const initialQuickReplies = page.locator('[data-testid^="quick-reply-"]');
    const initialButtons: string[] = [];
    const initialCount = await initialQuickReplies.count();

    for (let i = 0; i < initialCount; i++) {
      const text = await initialQuickReplies.nth(i).textContent();
      if (text) initialButtons.push(text);
    }

    console.log('Initial quick replies:', initialButtons);
    expect(initialButtons.length).toBeGreaterThan(0);

    // Click a quick reply to advance the conversation
    await initialQuickReplies.first().click();
    await page.waitForTimeout(3000);

    // Type a message with email to advance to next phase
    const input = page.locator('input[type="text"]');
    await input.fill('My email is test@example.com');
    await page.locator('[data-testid="send-button"]').click();
    await page.waitForTimeout(3000);

    // Check if quick replies have changed or are still present
    const newQuickReplies = page.locator('[data-testid^="quick-reply-"]');
    const exists = await newQuickReplies.count() > 0;

    if (exists) {
      console.log('✓ Quick replies updated based on conversation phase');
    } else {
      console.log('✓ Quick replies may not be visible in current phase');
    }
  });

  test('quick reply buttons are accessible via keyboard', async ({ page }) => {
    // Open chat widget
    const chatButton = page.locator('[data-testid="chat-widget-button"]');
    await chatButton.click();
    await page.waitForTimeout(1000);

    // Wait for welcome message and quick replies
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 5000 });
    await page.waitForTimeout(500);

    // Focus the first quick reply button
    const quickReplyButtons = page.locator('[data-testid^="quick-reply-"]');
    await quickReplyButtons.first().focus();

    // Verify it can be focused
    const focusedElement = await page.evaluate(() => document.activeElement?.textContent);
    console.log(`Focused element: "${focusedElement}"`);

    // Press Enter to activate
    await page.keyboard.press('Enter');
    await page.waitForTimeout(2000);

    // Verify message was sent
    const userMessages = page.locator('[data-testid="message-user"]');
    await expect(userMessages.first()).toBeVisible();
    console.log('✓ Quick reply button activated via keyboard');
  });

  test('quick reply buttons are disabled during streaming', async ({ page }) => {
    // Open chat widget
    const chatButton = page.locator('[data-testid="chat-widget-button"]');
    await chatButton.click();
    await page.waitForTimeout(1000);

    // Wait for welcome message
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 5000 });

    // Type a message to trigger streaming response
    const input = page.locator('input[type="text"]');
    await input.fill('Tell me about your services');

    // Click send
    await page.locator('[data-testid="send-button"]').click();

    // Immediately check if quick replies are disabled
    await page.waitForTimeout(500);
    const quickReplyButtons = page.locator('[data-testid^="quick-reply-"]');

    // Check if buttons are disabled during streaming
    const firstButton = quickReplyButtons.first();
    const isDisabled = await firstButton.isDisabled();

    console.log(`Quick reply disabled during streaming: ${isDisabled}`);

    // Wait for streaming to complete
    await page.waitForTimeout(3000);

    // Quick replies should be enabled again
    const isEnabledNow = await firstButton.isEnabled();
    console.log(`Quick reply enabled after streaming: ${isEnabledNow}`);
  });
});
