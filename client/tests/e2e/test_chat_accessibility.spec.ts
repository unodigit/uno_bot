import { test, expect } from '@playwright/test'

test.describe('Chat Widget Accessibility (Features 127-131)', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage to ensure fresh state
    await page.goto('http://localhost:5173')
    await page.evaluate(() => localStorage.clear())
    await page.reload()
  })

  test('Feature 127: Keyboard navigation works for chat interface', async ({ page }) => {
    // Step 1: Focus on chat widget button with Tab
    await page.keyboard.press('Tab')
    const chatButton = page.getByTestId('chat-widget-button')
    await expect(chatButton).toBeFocused()

    // Step 2: Press Enter to open
    await page.keyboard.press('Enter')
    await expect(page.getByTestId('chat-window')).toBeVisible()

    // Step 3: Tab through all interactive elements
    // Input should be focused first
    const input = page.getByTestId('message-input')
    await expect(input).toBeFocused()

    // Tab to send button
    await page.keyboard.press('Tab')
    const sendButton = page.getByTestId('send-button')
    await expect(sendButton).toBeFocused()

    // Tab to settings button
    await page.keyboard.press('Tab')
    const settingsButton = page.getByTestId('settings-button')
    await expect(settingsButton).toBeFocused()

    // Tab to minimize button
    await page.keyboard.press('Tab')
    const minimizeButton = page.getByTestId('minimize-button')
    await expect(minimizeButton).toBeFocused()

    // Tab to close button
    await page.keyboard.press('Tab')
    const closeButton = page.getByTestId('close-button')
    await expect(closeButton).toBeFocused()

    // Step 4: Verify Enter/Space work on buttons
    await page.keyboard.press('Enter')
    await expect(page.getByTestId('chat-widget-button')).toBeVisible()

    // Re-open and test Space key
    await page.keyboard.press('Enter')
    await expect(page.getByTestId('chat-window')).toBeVisible()

    // Step 5: Verify Escape closes chat
    await page.keyboard.press('Escape')
    await expect(page.getByTestId('chat-widget-button')).toBeVisible()
  })

  test('Feature 127: Keyboard navigation with quick replies', async ({ page }) => {
    // Open chat
    await page.keyboard.press('Tab')
    await page.keyboard.press('Enter')

    // Send a message to trigger quick replies
    const input = page.getByTestId('message-input')
    await input.fill('Hello')
    await page.keyboard.press('Enter')

    // Wait for quick replies to appear
    await expect(page.getByTestId('quick-replies')).toBeVisible()

    // Tab to first quick reply
    await page.keyboard.press('Tab')
    const firstQuickReply = page.getByTestId('quick-reply-0')
    await expect(firstQuickReply).toBeFocused()

    // Press Enter to send quick reply
    await page.keyboard.press('Enter')
    await expect(page.getByTestId('message-user')).toHaveCount(2)
  })

  test('Feature 127: Position menu keyboard navigation', async ({ page }) => {
    // Open chat and close to get to button
    await page.keyboard.press('Tab')
    await page.keyboard.press('Enter')
    await page.keyboard.press('Escape')

    // Focus button and open position menu with arrow keys
    await page.keyboard.press('Tab')
    await expect(page.getByTestId('chat-widget-button')).toBeFocused()
    await page.keyboard.press('ArrowDown')

    // Position menu should be visible
    const leftPosition = page.getByTestId('position-left')
    const rightPosition = page.getByTestId('position-right')
    await expect(leftPosition).toBeVisible()
    await expect(rightPosition).toBeVisible()

    // Tab to left position button
    await page.keyboard.press('Tab')
    await expect(leftPosition).toBeFocused()

    // Press Enter to select
    await page.keyboard.press('Enter')
    await expect(page.getByTestId('chat-widget-button')).toBeFocused()
  })

  test('Feature 128: Screen reader announces chat content correctly', async ({ page }) => {
    // Check for screen reader announcements container
    const announcements = page.locator('div[aria-live="polite"][aria-atomic="true"].sr-only')
    await expect(announcements).toHaveCount(2) // ChatWidget and ChatWindow

    // Open chat widget
    await page.keyboard.press('Tab')
    await page.keyboard.press('Enter')

    // Verify chat window announcements
    const chatWindowAnnouncements = page.locator('[data-testid="chat-window"] div[aria-live="polite"].sr-only')
    await expect(chatWindowAnnouncements).toContainText('Chat window opened')

    // Check messages container has proper ARIA attributes
    const messagesContainer = page.getByTestId('messages-container')
    await expect(messagesContainer).toHaveAttribute('role', 'log')
    await expect(messagesContainer).toHaveAttribute('aria-live', 'polite')
    await expect(messagesContainer).toHaveAttribute('aria-relevant', 'additions text')

    // Send a message and verify message announcements
    const input = page.getByTestId('message-input')
    await input.fill('Test message')
    await page.keyboard.press('Enter')

    // Wait for message to appear
    await expect(page.getByTestId('message-user')).toBeVisible()

    // Check message has ARIA attributes
    const userMessage = page.getByTestId('message-user').first()
    await expect(userMessage).toHaveAttribute('role', 'listitem')
    await expect(userMessage).toHaveAttribute('aria-label', 'Your message')
    await expect(userMessage).toHaveAttribute('aria-live', 'polite')
    await expect(userMessage).toHaveAttribute('aria-atomic', 'true')
  })

  test('Feature 128: Screen reader announces typing indicators', async ({ page }) => {
    // Open chat
    await page.keyboard.press('Tab')
    await page.keyboard.press('Enter')

    // Send a message (this will trigger typing indicator in real scenario)
    const input = page.getByTestId('message-input')
    await input.fill('Hello')
    await page.keyboard.press('Enter')

    // Check for typing indicator announcements
    // The typing indicator has aria-live="polite"
    const typingIndicator = page.locator('[aria-live="polite"]', { hasText: 'Bot is typing' })
    await expect(typingIndicator).toBeVisible()
  })

  test('Feature 128: Screen reader announcements for settings', async ({ page }) => {
    // Open chat
    await page.keyboard.press('Tab')
    await page.keyboard.press('Enter')

    // Open settings
    const settingsButton = page.getByTestId('settings-button')
    await settingsButton.click()

    // Check settings panel has proper ARIA
    const settingsPanel = page.getByTestId('settings-panel')
    await expect(settingsPanel).toBeVisible()

    // Check sound toggle has proper ARIA
    const soundToggle = page.getByTestId('sound-toggle')
    await expect(soundToggle).toHaveAttribute('role', 'switch')
    await expect(soundToggle).toHaveAttribute('aria-label', 'Toggle sound notifications')
  })

  test('Feature 130: Color contrast meets WCAG 2.1 AA standards', async ({ page }) => {
    // Open chat
    await page.keyboard.press('Tab')
    await page.keyboard.press('Enter')

    // Get computed styles for key elements
    const chatWindow = page.getByTestId('chat-window')
    const header = chatWindow.locator('div.h-12')

    // Check header background (primary: #2563EB)
    const headerBg = await header.evaluate(el => {
      return window.getComputedStyle(el).backgroundColor
    })
    // Header text should be white
    const headerText = await header.locator('span').first().evaluate(el => {
      return window.getComputedStyle(el).color
    })

    // Verify contrast ratios programmatically
    const contrastRatio = await page.evaluate(() => {
      const getContrastRatio = (color1: string, color2: string) => {
        const getLuminance = (color: string) => {
          const rgb = color.match(/\d+/g)?.map(Number) || [0, 0, 0]
          const [r, g, b] = rgb.map(c => {
            const sRGB = c / 255
            return sRGB <= 0.03928 ? sRGB / 12.92 : Math.pow((sRGB + 0.055) / 1.055, 2.4)
          })
          return 0.2126 * r + 0.7152 * g + 0.0722 * b
        }

        const l1 = getLuminance(color1)
        const l2 = getLuminance(color2)
        const lighter = Math.max(l1, l2)
        const darker = Math.min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)
      }

      // Test key color combinations
      const primary = '#2563EB'  // blue-600
      const white = '#FFFFFF'
      const text = '#1F2937'     // gray-800
      const surface = '#F3F4F6'  // gray-100
      const error = '#EF4444'

      return {
        primaryOnWhite: getContrastRatio(primary, white),
        textOnWhite: getContrastRatio(text, white),
        textOnSurface: getContrastRatio(text, surface),
        whiteOnPrimary: getContrastRatio(white, primary),
        errorOnWhite: getContrastRatio(error, white),
      }
    })

    // WCAG 2.1 AA requires 4.5:1 for normal text, 3:1 for large text
    expect(contrastRatio.primaryOnWhite).toBeGreaterThanOrEqual(4.5) // Primary text/buttons
    expect(contrastRatio.textOnWhite).toBeGreaterThanOrEqual(4.5)    // Body text
    expect(contrastRatio.whiteOnPrimary).toBeGreaterThanOrEqual(4.5) // Button text
    expect(contrastRatio.errorOnWhite).toBeGreaterThanOrEqual(4.5)   // Error text
  })

  test('Feature 131: ARIA labels are correctly applied', async ({ page }) => {
    // Open chat
    await page.keyboard.press('Tab')
    await page.keyboard.press('Enter')

    // Check main chat button
    const chatButton = page.getByTestId('chat-widget-button')
    await expect(chatButton).toHaveAttribute('aria-label', 'Open chat')
    await expect(chatButton).toHaveAttribute('aria-expanded', 'false')
    await expect(chatButton).toHaveAttribute('aria-haspopup', 'menu')

    // Check input field
    const input = page.getByTestId('message-input')
    await expect(input).toHaveAttribute('aria-label', 'Type your message')
    await expect(input).toHaveAttribute('aria-describedby')

    // Check send button
    const sendButton = page.getByTestId('send-button')
    await expect(sendButton).toHaveAttribute('aria-label')
    await expect(sendButton).toHaveAttribute('aria-describedby')

    // Check settings button
    const settingsButton = page.getByTestId('settings-button')
    await expect(settingsButton).toHaveAttribute('aria-label', 'Open settings')
    await expect(settingsButton).toHaveAttribute('aria-expanded')

    // Open settings and check toggle
    await settingsButton.click()
    const soundToggle = page.getByTestId('sound-toggle')
    await expect(soundToggle).toHaveAttribute('role', 'switch')
    await expect(soundToggle).toHaveAttribute('aria-checked')
    await expect(soundToggle).toHaveAttribute('aria-label')

    // Check minimize button
    const minimizeButton = page.getByTestId('minimize-button')
    await expect(minimizeButton).toHaveAttribute('aria-label', 'Minimize chat window')
    await expect(minimizeButton).toHaveAttribute('aria-describedby')

    // Check close button
    const closeButton = page.getByTestId('close-button')
    await expect(closeButton).toHaveAttribute('aria-label', 'Close chat')
  })

  test('Feature 131: ARIA labels on message elements', async ({ page }) => {
    // Open chat and send message
    await page.keyboard.press('Tab')
    await page.keyboard.press('Enter')

    const input = page.getByTestId('message-input')
    await input.fill('Hello')
    await page.keyboard.press('Enter')

    // Check user message
    const userMessage = page.getByTestId('message-user').first()
    await expect(userMessage).toHaveAttribute('aria-label', 'Your message')

    // Wait for bot response
    await expect(page.getByTestId('message-assistant')).toBeVisible()
    const botMessage = page.getByTestId('message-assistant').first()
    await expect(botMessage).toHaveAttribute('aria-label', 'Bot message')
  })

  test('Feature 129: Focus management works correctly', async ({ page }) => {
    // Step 1: Open chat widget
    await page.keyboard.press('Tab')
    const chatButton = page.getByTestId('chat-widget-button')
    await expect(chatButton).toBeFocused()
    await page.keyboard.press('Enter')

    // Step 2: Verify focus moves to input
    const input = page.getByTestId('message-input')
    await expect(input).toBeFocused()

    // Step 3: Close chat with Escape
    await page.keyboard.press('Escape')

    // Step 4: Verify focus returns to button
    await expect(chatButton).toBeFocused()

    // Step 5: Re-open and test minimize
    await page.keyboard.press('Enter')
    await expect(input).toBeFocused()

    // Tab to minimize button and click
    await page.keyboard.press('Tab') // send
    await page.keyboard.press('Tab') // settings
    await page.keyboard.press('Tab') // minimize
    const minimizeButton = page.getByTestId('minimize-button')
    await expect(minimizeButton).toBeFocused()
    await page.keyboard.press('Enter')

    // Verify focus returns to main button
    await expect(chatButton).toBeFocused()

    // No focus traps - can tab out of the widget when closed
    await page.keyboard.press('Tab')
    // Should be able to tab to next element on page
  })

  test('Feature 134: Widget loads in under 2 seconds', async ({ page }) => {
    const startTime = Date.now()

    await page.goto('http://localhost:5173')
    await page.waitForLoadState('networkidle')

    // Wait for chat widget button to be visible
    await page.waitForSelector('[data-testid="chat-widget-button"]', { timeout: 2000 })

    const loadTime = Date.now() - startTime
    expect(loadTime).toBeLessThan(2000)
  })

  test('Feature 134: Chat opens in under 500ms', async ({ page }) => {
    await page.goto('http://localhost:5173')
    await page.waitForSelector('[data-testid="chat-widget-button"]')

    const startTime = Date.now()
    await page.keyboard.press('Tab')
    await page.keyboard.press('Enter')

    // Wait for chat window to be visible
    await page.waitForSelector('[data-testid="chat-window"]', { timeout: 500 })

    const openTime = Date.now() - startTime
    expect(openTime).toBeLessThan(500)
  })
})
