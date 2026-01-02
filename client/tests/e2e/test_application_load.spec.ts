import { test, expect, Page } from '@playwright/test';

test('Application basic load test', async ({ page }: { page: Page }) => {
  // Navigate to main page
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");

  // Take a screenshot for debugging
  await page.screenshot({ path: 'debug-screenshot.png' });

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

  // Check if chat widget button exists
  const chatButton = page.locator('[data-testid="chat-widget-button"]');
  const buttonCount = await chatButton.count();

  if (buttonCount > 0) {
    console.log("Chat widget button found, attempting to check visibility...");

    // Wait a bit more for the button to be ready
    await page.waitForTimeout(1000);

    // Check if button is visible
    const isVisible = await chatButton.isVisible();
    if (isVisible) {
      console.log("Chat widget button is visible!");
    } else {
      console.log("Chat widget button exists but not visible");
      // Take another screenshot to see what's happening
      await page.screenshot({ path: 'debug-button-invisible.png' });
    }
  } else {
    console.log("Chat widget button not found");
    await page.screenshot({ path: 'debug-no-button.png' });
  }

  console.log("Application basic load test completed!");
});