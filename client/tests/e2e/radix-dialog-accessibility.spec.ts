import { test, expect } from '@playwright/test'

test.describe('Radix UI Dialog Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the dialog demo page
    await page.goto('http://localhost:5173/dialog-demo')
  })

  test('Dialog should have proper ARIA attributes', async ({ page }) => {
    // Open the dialog
    await page.click('button:has-text("Open Dialog")')

    // Wait for dialog to appear
    await page.waitForSelector('[role="dialog"]')

    // Check for proper ARIA attributes
    const dialog = page.locator('[role="dialog"]')
    await expect(dialog).toHaveAttribute('aria-modal', 'true')

    // Check for aria-labelledby pointing to title
    const dialogId = await dialog.getAttribute('aria-labelledby')
    expect(dialogId).toBeTruthy()

    // Verify the title element exists with matching id
    const title = page.locator(`#${dialogId}`)
    await expect(title).toBeVisible()

    // Check that backdrop is present
    const backdrop = page.locator('[data-state="open"]').locator('.fixed.inset-0')
    await expect(backdrop).toBeVisible()
  })

  test('Dialog should trap focus within modal', async ({ page }) => {
    // Open dialog
    await page.click('button:has-text("Open Dialog")')
    await page.waitForSelector('[role="dialog"]')

    // Focus should be trapped inside dialog
    const firstInput = page.locator('[role="dialog"] input').first()
    await firstInput.focus()

    // Press Tab multiple times - focus should cycle within dialog
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab')
      const withinDialog = await page.evaluate(() => {
        const active = document.activeElement
        return active?.closest('[role="dialog"]') !== null
      })
      expect(withinDialog).toBeTruthy()
    }
  })

  test('Escape key should close the dialog', async ({ page }) => {
    // Open dialog
    await page.click('button:has-text("Open Dialog")')
    await page.waitForSelector('[role="dialog"]')

    // Verify dialog is open
    let dialogVisible = await page.locator('[role="dialog"]').isVisible()
    expect(dialogVisible).toBeTruthy()

    // Press Escape
    await page.keyboard.press('Escape')

    // Wait for dialog to close
    await page.waitForSelector('[role="dialog"]', { state: 'hidden', timeout: 3000 })

    // Verify dialog is closed
    dialogVisible = await page.locator('[role="dialog"]').isVisible().catch(() => false)
    expect(dialogVisible).toBeFalsy()
  })

  test('Clicking overlay should close the dialog', async ({ page }) => {
    // Open dialog
    await page.click('button:has-text("Open Dialog")')
    await page.waitForSelector('[role="dialog"]')

    // Click on overlay (outside dialog content)
    const overlay = page.locator('[data-state="open"].fixed.inset-0')
    await overlay.click({ force: true })

    // Wait for dialog to close
    await page.waitForSelector('[role="dialog"]', { state: 'hidden', timeout: 3000 })

    // Verify dialog is closed
    const dialogVisible = await page.locator('[role="dialog"]').isVisible().catch(() => false)
    expect(dialogVisible).toBeFalsy()
  })

  test('Close button should be accessible via keyboard', async ({ page }) => {
    // Open dialog
    await page.click('button:has-text("Open Dialog")')
    await page.waitForSelector('[role="dialog"]')

    // Tab through elements - close button should be reachable
    for (let i = 0; i < 15; i++) {
      await page.keyboard.press('Tab')
      const isCloseButton = await page.evaluate(() => {
        return document.activeElement?.getAttribute('data-state') === 'closed'
      })
      if (isCloseButton) {
        // Found the close button, press Enter to close
        await page.keyboard.press('Enter')
        break
      }
    }

    // Verify dialog is closed
    await page.waitForSelector('[role="dialog"]', { state: 'hidden', timeout: 3000 })
    const dialogVisible = await page.locator('[role="dialog"]').isVisible().catch(() => false)
    expect(dialogVisible).toBeFalsy()
  })

  test('Dialog should restore focus to trigger after closing', async ({ page }) => {
    // Get the Open Dialog button
    const openButton = page.locator('button:has-text("Open Dialog")')

    // Click to open dialog
    await openButton.click()
    await page.waitForSelector('[role="dialog"]')

    // Close dialog with Escape
    await page.keyboard.press('Escape')
    await page.waitForSelector('[role="dialog"]', { state: 'hidden', timeout: 3000 })

    // Check if focus returned to trigger button
    const focusedElement = await page.evaluate(() => document.activeElement?.textContent)
    expect(focusedElement).toContain('Open Dialog')
  })

  test('All interactive elements should be keyboard accessible', async ({ page }) => {
    // Open dialog
    await page.click('button:has-text("Open Dialog")')
    await page.waitForSelector('[role="dialog"]')

    // Check that all buttons have accessible names
    const buttons = page.locator('[role="dialog"] button')
    const count = await buttons.count()

    for (let i = 0; i < count; i++) {
      const button = buttons.nth(i)
      const hasAccessibleName = await button.evaluate((el) => {
        return !!(el.getAttribute('aria-label') ||
                  el.getAttribute('title') ||
                  el.textContent?.trim())
      })
      expect(hasAccessibleName).toBeTruthy()
    }

    // Check that inputs have labels
    const inputs = page.locator('[role="dialog"] input[type="text"]')
    const inputCount = await inputs.count()

    for (let i = 0; i < inputCount; i++) {
      const input = inputs.nth(i)
      // Inputs should have placeholder or be labelable
      const hasPlaceholder = await input.evaluate((el) => !!el.getAttribute('placeholder'))
      expect(hasPlaceholder).toBeTruthy()
    }
  })

  test('Dialog description should be associated', async ({ page }) => {
    // Open dialog
    await page.click('button:has-text("Open Dialog")')
    await page.waitForSelector('[role="dialog"]')

    // Check for aria-describedby
    const dialog = page.locator('[role="dialog"]')
    const describedBy = await dialog.getAttribute('aria-describedby')
    expect(describedBy).toBeTruthy()

    // Verify the description element exists
    const description = page.locator(`#${describedBy}`)
    await expect(description).toBeVisible()
  })
})
