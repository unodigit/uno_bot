/**
 * Test helpers for UnoBot E2E tests
 */

import type { Page } from '@playwright/test';

export interface TestUser {
  name: string;
  email: string;
  visitorId: string;
}

export function generateTestUser(): TestUser {
  const timestamp = Date.now();
  return {
    name: `Test User ${timestamp}`,
    email: `test${timestamp}@example.com`,
    visitorId: `test_visitor_${timestamp}`,
  };
}

/**
 * Wait for an API response with a specific URL pattern
 */
export async function waitForApiResponse(
  page: Page,
  urlPattern: string | RegExp,
  timeout = 10000
) {
  return page.waitForResponse(
    (response) => response.url().includes(urlPattern) && response.ok(),
    { timeout }
  );
}

/**
 * Complete a basic conversation to enable booking flow
 */
export async function completeBasicConversation(
  page: Page,
  user: TestUser
) {
  const messageInput = page.getByTestId('message-input');
  const sendButton = page.getByTestId('send-button');

  // Send initial greeting
  await messageInput.fill('Hello');
  await sendButton.click();
  await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 15000 });

  // Send company info
  await messageInput.fill('I work at Acme Corp');
  await sendButton.click();
  await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 15000 });

  // Send industry
  await messageInput.fill('Tech industry');
  await sendButton.click();
  await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 15000 });

  // Send budget
  await messageInput.fill('Budget: $25k-$100k');
  await sendButton.click();
  await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 15000 });

  // Send timeline
  await messageInput.fill('Timeline: 1-3 months');
  await sendButton.click();
  await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 15000 });
}

/**
 * Match experts through the chat flow
 */
export async function matchExperts(page: Page) {
  const matchExpertsButton = page.getByTestId('match-experts-button');
  await matchExpertsButton.waitFor({ state: 'visible', timeout: 10000 });
  await matchExpertsButton.click();

  // Wait for matching to complete
  await page.waitForSelector('[data-testid="expert-matching"]', { timeout: 5000 });
  await page.waitForSelector('[data-testid="expert-matching"]', { state: 'hidden', timeout: 30000 });

  // Verify expert list
  await page.waitForSelector('[data-testid="expert-match-container"]', { timeout: 10000 });
}

/**
 * Book the first available expert
 */
export async function bookFirstExpert(page: Page) {
  const bookButtons = page.getByRole('button', { name: /book/i });
  await bookButtons.first().waitFor({ state: 'visible', timeout: 10000 });
  await bookButtons.first().click();
}

/**
 * Select the first available time slot
 */
export async function selectFirstTimeSlot(page: Page) {
  await page.waitForSelector('button[data-testid="time-slot-button"]', { timeout: 10000 });
  const timeSlotButtons = page.locator('button[data-testid="time-slot-button"]');
  await timeSlotButtons.first().click();
}

/**
 * Fill and submit booking form
 */
export async function submitBookingForm(page: Page, user: TestUser) {
  await page.waitForSelector('text=Confirm Booking', { timeout: 10000 });

  await page.getByLabel('Your Name').fill(user.name);
  await page.getByLabel('Email Address').fill(user.email);

  const submitButton = page.getByRole('button', { name: /confirm booking/i });
  await submitButton.waitFor({ state: 'visible' });
  await submitButton.click();
}

/**
 * Verify booking confirmation
 */
export async function verifyBookingConfirmation(page: Page, user: TestUser) {
  await page.waitForSelector('text=Booking Confirmed!', { timeout: 15000 });
  await page.waitForSelector(`text=${user.name}`, { timeout: 5000 });
  await page.waitForSelector(`text=${user.email}`, { timeout: 5000 });
}

/**
 * Complete full booking flow
 */
export async function completeBookingFlow(page: Page, user: TestUser) {
  await completeBasicConversation(page, user);
  await matchExperts(page);
  await bookFirstExpert(page);
  await selectFirstTimeSlot(page);
  await submitBookingForm(page, user);
  await verifyBookingConfirmation(page, user);
}
