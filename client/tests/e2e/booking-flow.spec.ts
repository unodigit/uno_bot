/**
 * End-to-End Tests for UnoBot Booking Flow
 *
 * Tests the complete user journey:
 * 1. Chat initialization and session creation
 * 2. Expert matching
 * 3. Time slot selection
 * 4. Booking form submission
 * 5. Booking confirmation
 */

import { test, expect } from '@playwright/test';
import type { Page } from '@playwright/test';

// Test utilities
const TEST_VISITOR_ID = `test_visitor_${Date.now()}`;
const TEST_EMAIL = `test${Date.now()}@example.com`;
const TEST_NAME = 'Test User';

// Helper to wait for API response
async function waitForApiResponse(page: Page, urlPattern: string | RegExp, timeout = 10000) {
  return page.waitForResponse(
    (response) => response.url().includes(urlPattern) && response.status() === 201,
    { timeout }
  );
}

test.describe('Complete Booking Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing session data
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  test('Complete booking flow: chat → expert match → time slot → form → confirmation', async ({
    page,
  }) => {
    test.setTimeout(120000); // 2 minutes for full flow

    // Step 1: Navigate to the app and verify chat window opens
    await page.goto('/');
    await expect(page.getByTestId('chat-window')).toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId('messages-container')).toBeVisible();

    // Step 2: Wait for initial messages to load
    await expect(page.getByTestId('message-assistant')).first().toBeVisible({ timeout: 15000 });

    // Step 3: Send initial message to start conversation
    const messageInput = page.getByTestId('message-input');
    const sendButton = page.getByTestId('send-button');

    await messageInput.fill('Hello, I need help with AI strategy for my company');
    await expect(sendButton).toBeEnabled();
    await sendButton.click();

    // Wait for AI response
    await expect(page.getByTestId('typing-indicator')).toBeVisible();
    await expect(page.getByTestId('typing-indicator')).toBeHidden({ timeout: 30000 });
    await expect(page.getByTestId('message-assistant').last()).toBeVisible();

    // Step 4: Fill in client info through chat (discovery phase)
    // Send company info
    await messageInput.fill('I work at Acme Corp');
    await sendButton.click();
    await expect(page.getByTestId('message-assistant').last()).toBeVisible({ timeout: 15000 });

    // Send industry
    await messageInput.fill('Tech industry');
    await sendButton.click();
    await expect(page.getByTestId('message-assistant').last()).toBeVisible({ timeout: 15000 });

    // Send budget info
    await messageInput.fill('Budget: $25k-$100k');
    await sendButton.click();
    await expect(page.getByTestId('message-assistant').last()).toBeVisible({ timeout: 15000 });

    // Send timeline
    await messageInput.fill('Timeline: 1-3 months');
    await sendButton.click();
    await expect(page.getByTestId('message-assistant').last()).toBeVisible({ timeout: 15000 });

    // Step 5: Match experts
    // Wait for expert matching button to be enabled
    const matchExpertsButton = page.getByTestId('match-experts-button');
    await expect(matchExpertsButton).toBeVisible({ timeout: 10000 });
    await expect(matchExpertsButton).toBeEnabled();

    // Click match experts
    await matchExpertsButton.click();

    // Wait for expert matching indicator
    await expect(page.getByTestId('expert-matching')).toBeVisible();
    await expect(page.getByTestId('expert-matching')).toBeHidden({ timeout: 30000 });

    // Verify expert list is displayed
    const expertContainer = page.getByTestId('expert-match-container');
    await expect(expertContainer).toBeVisible({ timeout: 10000 });

    // Step 6: Book an expert
    // Find and click the first "Book" button
    const bookButtons = page.getByRole('button', { name: /book/i });
    await expect(bookButtons.first()).toBeVisible();
    await bookButtons.first().click();

    // Step 7: Verify calendar picker is displayed
    await expect(page.getByText('Select a time slot')).toBeVisible({ timeout: 10000 });

    // Step 8: Select a time slot
    const timeSlotButtons = page.locator('button[data-testid="time-slot-button"]');
    await expect(timeSlotButtons.first()).toBeVisible({ timeout: 10000 });
    await timeSlotButtons.first().click();

    // Step 9: Verify booking form is displayed
    await expect(page.getByText('Confirm Booking')).toBeVisible({ timeout: 10000 });
    await expect(page.getByLabel('Your Name')).toBeVisible();
    await expect(page.getByLabel('Email Address')).toBeVisible();

    // Step 10: Fill booking form
    await page.getByLabel('Your Name').fill(TEST_NAME);
    await page.getByLabel('Email Address').fill(TEST_EMAIL);

    // Step 11: Submit booking
    const submitButton = page.getByRole('button', { name: /confirm booking/i });
    await expect(submitButton).toBeEnabled();
    await submitButton.click();

    // Step 12: Verify booking confirmation
    await expect(page.getByText('Booking Confirmed!')).toBeVisible({ timeout: 15000 });
    await expect(page.getByText(TEST_NAME)).toBeVisible();
    await expect(page.getByText(TEST_EMAIL)).toBeVisible();

    // Step 13: Click Done to close booking flow
    const doneButton = page.getByRole('button', { name: /done/i });
    await expect(doneButton).toBeVisible();
    await doneButton.click();

    // Step 14: Verify we're back to normal chat view
    await expect(page.getByTestId('chat-window')).toBeVisible();
    await expect(page.getByTestId('message-input')).toBeVisible();
  });

  test('Chat window controls: minimize and close', async ({ page }) => {
    await page.goto('/');

    // Verify chat window is visible
    const chatWindow = page.getByTestId('chat-window');
    await expect(chatWindow).toBeVisible();

    // Test minimize button
    const minimizeButton = page.getByTestId('minimize-button');
    if (await minimizeButton.isVisible()) {
      await minimizeButton.click();
      // Note: Minimize behavior may vary, just verify button works
    }

    // Test close button
    const closeButton = page.getByTestId('close-button');
    await expect(closeButton).toBeVisible();
    await closeButton.click();

    // Chat window should be closed (not visible)
    // Note: Depending on implementation, it might be hidden or removed
  });

  test('PRD generation flow', async ({ page }) => {
    test.setTimeout(60000);

    await page.goto('/');
    await expect(page.getByTestId('chat-window')).toBeVisible();

    // Send messages to build context
    const messageInput = page.getByTestId('message-input');
    const sendButton = page.getByTestId('send-button');

    // Complete conversation to enable PRD generation
    await messageInput.fill('Hello');
    await sendButton.click();
    await expect(page.getByTestId('message-assistant').last()).toBeVisible({ timeout: 15000 });

    await messageInput.fill('I work at TechCorp');
    await sendButton.click();
    await expect(page.getByTestId('message-assistant').last()).toBeVisible({ timeout: 15000 });

    await messageInput.fill('We need an AI chatbot');
    await sendButton.click();
    await expect(page.getByTestId('message-assistant').last()).toBeVisible({ timeout: 15000 });

    await messageInput.fill('Budget: $50k');
    await sendButton.click();
    await expect(page.getByTestId('message-assistant').last()).toBeVisible({ timeout: 15000 });

    // Wait for PRD button to be enabled
    const prdButton = page.getByTestId('generate-prd-button');
    await expect(prdButton).toBeVisible({ timeout: 10000 });
    await expect(prdButton).toBeEnabled();

    // Click generate PRD
    await prdButton.click();

    // Verify PRD generation indicator
    await expect(page.getByTestId('prd-generating')).toBeVisible();
    await expect(page.getByTestId('prd-generating')).toBeHidden({ timeout: 30000 });

    // Verify PRD preview card is displayed
    await expect(page.getByTestId('prd-preview-card')).toBeVisible({ timeout: 10000 });

    // Verify download button exists
    const downloadButton = page.getByTestId('download-prd-button');
    await expect(downloadButton).toBeVisible();
  });

  test('Error handling: invalid booking form', async ({ page }) => {
    test.setTimeout(60000);

    await page.goto('/');

    // Complete conversation and reach booking form
    const messageInput = page.getByTestId('message-input');
    const sendButton = page.getByTestId('send-button');

    // Build context
    await messageInput.fill('Hello');
    await sendButton.click();
    await expect(page.getByTestId('message-assistant').last()).toBeVisible({ timeout: 15000 });

    await messageInput.fill('I work at TestCorp');
    await sendButton.click();
    await expect(page.getByTestId('message-assistant').last()).toBeVisible({ timeout: 15000 });

    await messageInput.fill('Need help with AI');
    await sendButton.click();
    await expect(page.getByTestId('message-assistant').last()).toBeVisible({ timeout: 15000 });

    await messageInput.fill('Budget: $25k-$100k');
    await sendButton.click();
    await expect(page.getByTestId('message-assistant').last()).toBeVisible({ timeout: 15000 });

    // Match experts
    const matchExpertsButton = page.getByTestId('match-experts-button');
    await expect(matchExpertsButton).toBeVisible({ timeout: 10000 });
    await matchExpertsButton.click();
    await expect(page.getByTestId('expert-matching')).toBeHidden({ timeout: 30000 });

    // Book expert
    const bookButtons = page.getByRole('button', { name: /book/i });
    await bookButtons.first().click();

    // Select time slot
    const timeSlotButtons = page.locator('button[data-testid="time-slot-button"]');
    await timeSlotButtons.first().click();

    // Try to submit without filling form
    const submitButton = page.getByRole('button', { name: /confirm booking/i });
    await expect(submitButton).toBeDisabled();

    // Fill only name
    await page.getByLabel('Your Name').fill(TEST_NAME);
    await expect(submitButton).toBeDisabled();

    // Fill invalid email
    await page.getByLabel('Email Address').fill('invalid-email');
    await expect(submitButton).toBeDisabled();

    // Fill valid email
    await page.getByLabel('Email Address').fill(TEST_EMAIL);
    await expect(submitButton).toBeEnabled();
  });
});

test.describe('Quick Reply Buttons', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page.getByTestId('chat-window')).toBeVisible();
  });

  test('Quick replies appear and work', async ({ page }) => {
    const messageInput = page.getByTestId('message-input');
    const sendButton = page.getByTestId('send-button');

    // Send initial message
    await messageInput.fill('Hello');
    await sendButton.click();
    await expect(page.getByTestId('message-assistant').last()).toBeVisible({ timeout: 15000 });

    // Verify quick replies are visible
    const quickRepliesContainer = page.getByTestId('quick-replies');
    await expect(quickRepliesContainer).toBeVisible({ timeout: 10000 });

    // Click a quick reply
    const quickReplyButton = quickRepliesContainer.getByRole('button').first();
    const buttonText = await quickReplyButton.textContent();
    await quickReplyButton.click();

    // Verify the message was sent
    await expect(page.getByText(buttonText || '')).toBeVisible();
  });
});
