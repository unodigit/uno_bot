import { test, expect, Page } from '@playwright/test';

test('Console error check', async ({ page }: { page: Page }) => {
  // Array to store console errors
  const consoleErrors: any[] = [];
  const consoleWarnings: any[] = [];

  // Capture console messages
  page.on("console", (msg) => {
    if (msg.type === "error") {
      consoleErrors.push({
        text: msg.text(),
        location: msg.location(),
        args: msg.args().map(arg => arg.toString())
      });
    } else if (msg.type === "warning") {
      consoleWarnings.push({
        text: msg.text(),
        location: msg.location(),
        args: msg.args().map(arg => arg.toString())
      });
    }
  });

  // Navigate to main page
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");

  // Wait a bit more to capture any delayed console messages
  await page.waitForTimeout(2000);

  // Verify page has loaded
  await expect(page.locator("body")).toBeVisible();

  // Check for chat widget button
  const chatButton = page.locator('[data-testid="chat-widget-button"]');
  const buttonExists = await chatButton.count() > 0;

  if (buttonExists) {
    console.log("Chat widget button found");
  } else {
    console.log("Chat widget button not found");
  }

  // Log console errors
  if (consoleErrors.length > 0) {
    console.log(`\n=== CONSOLE ERRORS (${consoleErrors.length}) ===`);
    consoleErrors.forEach((error, index) => {
      console.log(`Error ${index + 1}: ${error.text}`);
      if (error.location) {
        console.log(`  Location: ${error.location.url}:${error.location.lineNumber}:${error.location.columnNumber}`);
      }
      if (error.args.length > 0) {
        console.log(`  Args: ${error.args.join(', ')}`);
      }
    });
  } else {
    console.log("No console errors found");
  }

  // Log console warnings
  if (consoleWarnings.length > 0) {
    console.log(`\n=== CONSOLE WARNINGS (${consoleWarnings.length}) ===`);
    consoleWarnings.forEach((warning, index) => {
      console.log(`Warning ${index + 1}: ${warning.text}`);
      if (warning.location) {
        console.log(`  Location: ${warning.location.url}:${warning.location.lineNumber}:${warning.location.columnNumber}`);
      }
      if (warning.args.length > 0) {
        console.log(`  Args: ${warning.args.join(', ')}`);
      }
    });
  } else {
    console.log("No console warnings found");
  }

  // Report results
  console.log(`\n=== SUMMARY ===`);
  console.log(`Page loaded: ✓`);
  console.log(`Chat widget button exists: ${buttonExists ? '✓' : '✗'}`);
  console.log(`Console errors: ${consoleErrors.length === 0 ? '✓' : '✗ (' + consoleErrors.length + ')'}`);
  console.log(`Console warnings: ${consoleWarnings.length} (info only)`);

  // Test should pass if there are no console errors
  expect(consoleErrors.length).toBe(0);
});