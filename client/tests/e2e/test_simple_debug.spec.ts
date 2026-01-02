import { test, expect } from '@playwright/test';

test('debug - check if page loads', async ({ page }) => {
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");
  await page.screenshot({ path: 'debug-page-load.png' });

  // Check if chat button exists
  const chatButton = page.locator('[data-testid="chat-widget-button"]');
  const count = await chatButton.count();
  console.log(`Chat button count: ${count}`);

  if (count > 0) {
    const isVisible = await chatButton.isVisible();
    console.log(`Chat button visible: ${isVisible}`);

    // Click it
    await chatButton.click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'debug-after-click.png' });

    // Check if chat window is visible
    const chatWindow = page.locator('[data-testid="chat-window"]');
    const windowVisible = await chatWindow.isVisible();
    console.log(`Chat window visible: ${windowVisible}`);

    // Check if chat input exists
    const chatInput = page.locator('[data-testid="chat-input"]');
    const inputCount = await chatInput.count();
    console.log(`Chat input count: ${inputCount}`);

    if (inputCount > 0) {
      const inputVisible = await chatInput.isVisible();
      console.log(`Chat input visible: ${inputVisible}`);
    }
  }
});
