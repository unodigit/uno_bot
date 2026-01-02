import { test, expect, Page } from '@playwright/test';

test('Robust chat widget test', async ({ page }: { page: Page }) => {
  // Navigate to main page
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");

  // Check for console errors
  const pageErrors: any[] = [];
  page.on("console", (msg) => {
    if (msg.type === "error") {
      pageErrors.push(msg);
    }
  });

  // Verify page has loaded
  await expect(page.locator("body")).toBeVisible();

  // Check for any console errors
  expect(pageErrors).toHaveLength(0);

  // Test 1: Verify chat widget button exists and is visible (normal state)
  let chatButton = page.locator('[data-testid="chat-widget-button"]');
  let minimizedButton = page.locator('[data-testid="chat-widget-button-minimized"]');

  // Wait for one of the buttons to be visible
  await expect(chatButton.or(minimizedButton)).toBeVisible({ timeout: 10000 });

  // Determine which button is visible
  let isMinimized = false;
  if (await minimizedButton.isVisible()) {
    isMinimized = true;
    chatButton = minimizedButton;
    console.log("Chat is minimized, using minimized button");
  } else {
    console.log("Chat is normal, using normal button");
  }

  // Test 2: Click the chat widget button to open the chat
  await chatButton.click();

  // Test 3: Verify chat window opens
  const chatWindow = page.locator('[data-testid="chat-window"]');
  await expect(chatWindow).toBeVisible({ timeout: 10000 });

  // Test 4: Verify chat window has proper structure
  // Check for header elements
  const header = page.locator('.bg-primary').first(); // Header should have bg-primary class
  await expect(header).toBeVisible();

  // Test 5: Test minimize functionality
  const minimizeButton = page.locator('[data-testid="minimize-button"]');
  if (await minimizeButton.count() > 0) {
    // Wait for minimize button to be clickable
    await minimizeButton.waitFor({ state: 'visible', timeout: 5000 });
    await minimizeButton.click();

    // Wait for animation and check if minimized
    await page.waitForTimeout(1000);

    // The chat window should be hidden when minimized
    const isMinimizedAfter = await chatWindow.isVisible();
    expect(isMinimizedAfter).toBe(false);

    // Check that minimized button is now visible
    const newMinimizedButton = page.locator('[data-testid="chat-widget-button-minimized"]');
    await expect(newMinimizedButton).toBeVisible({ timeout: 5000 });
  }

  // Test 6: Open chat again using the minimized button
  const finalMinimizedButton = page.locator('[data-testid="chat-widget-button-minimized"]');
  if (await finalMinimizedButton.count() > 0) {
    await finalMinimizedButton.click();
    await expect(chatWindow).toBeVisible({ timeout: 5000 });
  }

  // Test 7: Test close functionality
  const closeButton = page.locator('[data-testid="close-button"]');
  await closeButton.click();

  // Wait for animation and check if closed
  await page.waitForTimeout(1000);

  // The chat window should be hidden when closed
  const isClosed = await chatWindow.isVisible();
  expect(isClosed).toBe(false);

  // Test 8: Verify button is still visible after closing
  const finalButton = page.locator('[data-testid="chat-widget-button"]').or(page.locator('[data-testid="chat-widget-button-minimized"]'));
  await expect(finalButton).toBeVisible();

  console.log("All robust chat widget functionality tests passed!");
});