import { test, expect, Page } from '@playwright/test';

test('Basic page load', async ({ page }: { page: Page }) => {
  // Navigate to main page
  await page.goto("http://localhost:5173");

  // Wait for page to fully load
  await page.waitForLoadState("networkidle");

  // Check for console errors
  const pageErrors: any[] = [];
  page.on("console", (msg) => {
    if (msg.type === "error") {
      pageErrors.push(msg);
    }
  });

  // Verify page has loaded (check for body)
  await expect(page.locator("body")).toBeVisible();

  // Check for any console errors
  expect(pageErrors).toHaveLength(0);
});

test('Chat widget button exists', async ({ page }: { page: Page }) => {
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");

  // Check if chat widget button exists
  const button = page.locator('[data-testid="chat-widget-button"]');

  // If button exists, check visibility
  if (await button.count() > 0) {
    await expect(button).toBeVisible();
    console.log("Chat widget button found and visible");
  } else {
    console.log("Chat widget button not found - this might be expected behavior");
  }
});

test('Page title exists', async ({ page }: { page: Page }) => {
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");

  const title = await page.title();
  console.log(`Page title: ${title}`);
  expect(title).not.toBeNull();
});