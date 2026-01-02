import { test, expect, Page } from '@playwright/test';
import { TestUser, generateTestUser, completeBasicConversation, matchExperts } from './helpers';

/**
 * Session Resume via Email Link E2E Tests
 *
 * These tests verify that users can:
 * 1. Start a conversation in the chat widget
 * 2. Get a session ID from localStorage
 * 3. Generate a resume URL with the session ID
 * 4. Navigate to the resume URL
 * 5. Verify that the chat window opens and shows previous conversation history
 */

test.describe('Session Resume via Email Link', () => {
  let testUser: TestUser;

  test.beforeEach(async ({ page }) => {
    testUser = generateTestUser();

    // Clear localStorage before each test
    await page.addInitScript(() => {
      localStorage.clear();
      sessionStorage.clear();
    });

    // Mock the API responses to simulate a real backend
    await mockAPIResponses(page);
  });

  test('should resume session with conversation history after navigating to resume URL', async ({ page }) => {
    // Step 1: Navigate to http://localhost:5180 (frontend)
    await page.goto('http://localhost:5173');

    // Step 2: Open the chat widget and send a test message
    const chatWidgetButton = page.getByTestId('chat-widget-button');
    await expect(chatWidgetButton).toBeVisible();
    await chatWidgetButton.click();

    // Wait for chat window to open
    const chatWindow = page.locator('[data-testid="chat-window"]');
    await expect(chatWindow).toBeVisible();

    // Wait for initial welcome message
    await expect(page.getByTestId('message-assistant')).toBeVisible();

    // Send first test message
    const messageInput = page.getByTestId('message-input');
    const sendButton = page.getByTestId('send-button');

    await messageInput.fill('Hello, I need help with my project');
    await sendButton.click();

    // Wait for the assistant response
    await expect(page.getByText('Hello, I need help with my project')).toBeVisible();
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 15000 });

    // Send second test message
    await messageInput.fill('My name is Test User');
    await sendButton.click();

    // Wait for response
    await expect(page.getByText('My name is Test User')).toBeVisible();
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 15000 });

    // Step 3: Get the session ID from localStorage
    const sessionId = await page.evaluate(() => {
      return localStorage.getItem('unobot_session_id');
    });

    expect(sessionId).toBeTruthy();
    expect(typeof sessionId).toBe('string');
    expect(sessionId?.length).toBeGreaterThan(0);

    console.log(`Generated session ID: ${sessionId}`);

    // Step 4: Generate a resume URL with the session ID
    const resumeUrl = `http://localhost:5173?session_id=${encodeURIComponent(sessionId!)}`;
    console.log(`Resume URL: ${resumeUrl}`);

    // Step 5: Navigate to the resume URL
    await page.goto(resumeUrl);

    // Mock API responses for the resumed session
    await mockResumeAPIResponses(page, sessionId!);

    // Step 6: Verify that the chat window opens and shows the previous conversation history
    // The chat widget should be visible
    await expect(chatWidgetButton).toBeVisible();

    // Open the chat widget
    await chatWidgetButton.click();
    await expect(chatWindow).toBeVisible();

    // Verify conversation history is preserved
    await expect(page.getByText('Hello, I need help with my project')).toBeVisible();
    await expect(page.getByText('My name is Test User')).toBeVisible();

    // Verify that we can still send new messages
    await messageInput.fill('This is a new message after resuming');
    await sendButton.click();

    // Verify the new message appears
    await expect(page.getByText('This is a new message after resuming')).toBeVisible();

    // Verify session ID is still in localStorage
    const resumedSessionId = await page.evaluate(() => {
      return localStorage.getItem('unobot_session_id');
    });

    expect(resumedSessionId).toBe(sessionId);
  });

  test('should handle session resume URL without opening chat widget automatically', async ({ page }) => {
    // Start with a fresh session
    await page.goto('http://localhost:5173');

    // Mock API responses
    await mockAPIResponses(page);

    // Open chat and send a message
    const chatWidgetButton = page.getByTestId('chat-widget-button');
    await chatWidgetButton.click();

    const messageInput = page.getByTestId('message-input');
    const sendButton = page.getByTestId('send-button');

    await messageInput.fill('Testing session resume functionality');
    await sendButton.click();

    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 15000 });

    // Get session ID
    const sessionId = await page.evaluate(() => {
      return localStorage.getItem('unobot_session_id');
    });

    expect(sessionId).toBeTruthy();

    // Navigate to resume URL
    const resumeUrl = `http://localhost:5173?session_id=${encodeURIComponent(sessionId!)}`;
    await page.goto(resumeUrl);

    // Mock API responses for resume
    await mockResumeAPIResponses(page, sessionId!);

    // Verify chat widget is closed initially (user must open it)
    await expect(chatWidgetButton).toBeVisible();

    // Chat window should not be open initially
    const chatWindow = page.locator('[data-testid="chat-window"]');
    await expect(chatWindow).not.toBeVisible();

    // User must manually open the chat to see the conversation
    await chatWidgetButton.click();
    await expect(chatWindow).toBeVisible();

    // Verify conversation history is preserved
    await expect(page.getByText('Testing session resume functionality')).toBeVisible();
  });

  test('should handle session ID from URL parameters on page load', async ({ page }) => {
    // Create a session first
    await page.goto('http://localhost:5173');
    await mockAPIResponses(page);

    const chatWidgetButton = page.getByTestId('chat-widget-button');
    await chatWidgetButton.click();

    const messageInput = page.getByTestId('message-input');
    await messageInput.fill('Initial message for URL parameter test');
    await page.getByTestId('send-button').click();

    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 15000 });

    const sessionId = await page.evaluate(() => {
      return localStorage.getItem('unobot_session_id');
    });

    expect(sessionId).toBeTruthy();

    // Navigate to page with session_id in URL
    const urlWithSessionId = `http://localhost:5173?session_id=${encodeURIComponent(sessionId!)}`;
    await page.goto(urlWithSessionId);

    await mockResumeAPIResponses(page, sessionId!);

    // The session should be loaded from URL parameter
    const storedSessionId = await page.evaluate(() => {
      return localStorage.getItem('unobot_session_id');
    });

    expect(storedSessionId).toBe(sessionId);

    // Chat widget should be available
    await expect(chatWidgetButton).toBeVisible();

    // Open chat to verify history
    await chatWidgetButton.click();
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await expect(page.getByText('Initial message for URL parameter test')).toBeVisible();
  });

  test('should handle invalid session ID gracefully', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await mockAPIResponses(page);

    // Navigate to URL with invalid session ID
    const invalidSessionId = 'invalid-session-id-12345';
    const urlWithInvalidSessionId = `http://localhost:5173?session_id=${encodeURIComponent(invalidSessionId)}`;
    await page.goto(urlWithInvalidSessionId);

    // Mock API to return 404 for invalid session
    await page.route('**/api/v1/sessions/invalid-session-id-12345/resume', route => {
      route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Session not found' })
      });
    });

    // Should fall back to creating a new session
    const chatWidgetButton = page.getByTestId('chat-widget-button');
    await chatWidgetButton.click();

    // Should work normally with a new session
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await expect(page.getByTestId('message-input')).toBeVisible();
  });

  test('should maintain session state across page refreshes', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await mockAPIResponses(page);

    // Start conversation
    const chatWidgetButton = page.getByTestId('chat-widget-button');
    await chatWidgetButton.click();

    const messageInput = page.getByTestId('message-input');
    await messageInput.fill('Message before refresh');
    await page.getByTestId('send-button').click();

    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 15000 });

    // Get session ID
    const sessionId = await page.evaluate(() => {
      return localStorage.getItem('unobot_session_id');
    });

    expect(sessionId).toBeTruthy();

    // Mock API responses for refresh
    await mockResumeAPIResponses(page, sessionId!);

    // Refresh the page
    await page.reload();

    // Verify session is restored from localStorage
    const refreshedSessionId = await page.evaluate(() => {
      return localStorage.getItem('unobot_session_id');
    });

    expect(refreshedSessionId).toBe(sessionId);

    // Open chat and verify history
    await chatWidgetButton.click();
    await expect(page.getByText('Message before refresh')).toBeVisible();
  });

  test('should handle multiple messages and complex conversation history', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await mockAPIResponses(page);

    // Start complex conversation
    const chatWidgetButton = page.getByTestId('chat-widget-button');
    await chatWidgetButton.click();

    const messageInput = page.getByTestId('message-input');
    const sendButton = page.getByTestId('send-button');

    // Send multiple messages
    const messages = [
      'I want to build an e-commerce platform',
      "My company is called TechCorp",
      'We need a mobile app and web dashboard',
      'Budget is around $50,000',
      'Timeline is 3 months'
    ];

    for (const message of messages) {
      await messageInput.fill(message);
      await sendButton.click();
      await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 15000 });
      await expect(page.getByText(message)).toBeVisible();
    }

    // Get session ID
    const sessionId = await page.evaluate(() => {
      return localStorage.getItem('unobot_session_id');
    });

    expect(sessionId).toBeTruthy();

    // Mock API responses for complex conversation
    await mockResumeAPIResponses(page, sessionId!, messages);

    // Navigate to resume URL
    const resumeUrl = `http://localhost:5173?session_id=${encodeURIComponent(sessionId!)}`;
    await page.goto(resumeUrl);

    // Open chat and verify all messages are preserved
    await chatWidgetButton.click();
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();

    // Verify all messages are present
    for (const message of messages) {
      await expect(page.getByText(message)).toBeVisible();
    }

    // Verify we can continue the conversation
    await messageInput.fill('Can you help me match with experts?');
    await sendButton.click();
    await page.waitForSelector('[data-testid="message-assistant"]', { timeout: 15000 });
    await expect(page.getByText('Can you help me match with experts?')).toBeVisible();
  });
});

/**
 * Mock API responses for initial session creation and messages
 */
async function mockAPIResponses(page: Page) {
  // Mock session creation
  await page.route('**/api/v1/sessions', route => {
    const mockSession = {
      id: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      visitor_id: `visitor_${Date.now()}`,
      messages: [
        {
          id: `msg_${Date.now()}`,
          session_id: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          role: 'assistant',
          content: "🎉 Welcome! I'm UnoBot, your AI business consultant from UnoDigit.\n\nTo get started, what's your name?",
          meta_data: { type: 'welcome' },
          created_at: new Date().toISOString(),
        }
      ],
      current_phase: 'greeting',
      client_info: {},
      business_context: {},
      qualification: {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockSession)
    });
  });

  // Mock message sending
  await page.route('**/api/v1/sessions/**/messages', route => {
    const url = route.request().url();
    const sessionId = url.split('/')[4]; // Extract session ID from URL

    const mockResponse = {
      id: `msg_${Date.now()}`,
      session_id: sessionId,
      role: 'assistant',
      content: "Thank you for your message. How can I help you further?",
      meta_data: {},
      created_at: new Date().toISOString(),
    };
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockResponse)
    });
  });

  // Mock session retrieval
  await page.route('**/api/v1/sessions/**', route => {
    const url = route.request().url();
    const sessionId = url.split('/')[4]; // Extract session ID from URL

    const mockSession = {
      id: sessionId,
      visitor_id: `visitor_${Date.now()}`,
      messages: [
        {
          id: `msg_${Date.now()}`,
          session_id: sessionId,
          role: 'assistant',
          content: "🎉 Welcome! I'm UnoBot, your AI business consultant from UnoDigit.\n\nTo get started, what's your name?",
          meta_data: { type: 'welcome' },
          created_at: new Date().toISOString(),
        }
      ],
      current_phase: 'greeting',
      client_info: {},
      business_context: {},
      qualification: {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockSession)
    });
  });

  // Mock session resume
  await page.route('**/api/v1/sessions/**/resume', route => {
    const url = route.request().url();
    const sessionId = url.split('/')[4]; // Extract session ID from URL

    const mockSession = {
      id: sessionId,
      visitor_id: `visitor_${Date.now()}`,
      messages: [
        {
          id: `msg_${Date.now()}`,
          session_id: sessionId,
          role: 'assistant',
          content: "🎉 Welcome! I'm UnoBot, your AI business consultant from UnoDigit.\n\nTo get started, what's your name?",
          meta_data: { type: 'welcome' },
          created_at: new Date().toISOString(),
        }
      ],
      current_phase: 'greeting',
      client_info: {},
      business_context: {},
      qualification: {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockSession)
    });
  });

  // Mock health check
  await page.route('**/api/v1/health', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok' })
    });
  });
}

/**
 * Mock API responses specifically for session resume
 */
async function mockResumeAPIResponses(page: Page, sessionId: string, messages?: string[]) {
  // Mock session creation with existing session data
  await page.route('**/api/v1/sessions', route => {
    const mockSession = {
      id: sessionId,
      visitor_id: `visitor_${Date.now()}`,
      messages: [
        {
          id: `msg_${Date.now()}`,
          session_id: sessionId,
          role: 'assistant',
          content: "🎉 Welcome! I'm UnoBot, your AI business consultant from UnoDigit.\n\nTo get started, what's your name?",
          meta_data: { type: 'welcome' },
          created_at: new Date().toISOString(),
        }
      ],
      current_phase: 'greeting',
      client_info: {},
      business_context: {},
      qualification: {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockSession)
    });
  });

  // Mock session resume with conversation history
  await page.route('**/api/v1/sessions/**/resume', route => {
    const mockSession = {
      id: sessionId,
      visitor_id: `visitor_${Date.now()}`,
      messages: [
        {
          id: `msg_${Date.now()}`,
          session_id: sessionId,
          role: 'assistant',
          content: "🎉 Welcome! I'm UnoBot, your AI business consultant from UnoDigit.\n\nTo get started, what's your name?",
          meta_data: { type: 'welcome' },
          created_at: new Date().toISOString(),
        }
      ],
      current_phase: 'greeting',
      client_info: {},
      business_context: {},
      qualification: {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Add previous conversation messages if provided
    if (messages && messages.length > 0) {
      messages.forEach((msg, index) => {
        mockSession.messages.push({
          id: `user_msg_${index}`,
          session_id: sessionId,
          role: 'user',
          content: msg,
          meta_data: {},
          created_at: new Date(Date.now() - (messages.length - index) * 1000).toISOString(),
        });
        mockSession.messages.push({
          id: `bot_msg_${index}`,
          session_id: sessionId,
          role: 'assistant',
          content: `Response to: ${msg}`,
          meta_data: {},
          created_at: new Date(Date.now() - (messages.length - index) * 1000 + 500).toISOString(),
        });
      });
    }

    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockSession)
    });
  });

  // Mock session retrieval with conversation history
  await page.route('**/api/v1/sessions/**', route => {
    const url = route.request().url();
    const sessionPathId = url.split('/')[4]; // Extract session ID from URL

    const mockSession = {
      id: sessionPathId,
      visitor_id: `visitor_${Date.now()}`,
      messages: [
        {
          id: `msg_${Date.now()}`,
          session_id: sessionPathId,
          role: 'assistant',
          content: "🎉 Welcome! I'm UnoBot, your AI business consultant from UnoDigit.\n\nTo get started, what's your name?",
          meta_data: { type: 'welcome' },
          created_at: new Date().toISOString(),
        }
      ],
      current_phase: 'greeting',
      client_info: {},
      business_context: {},
      qualification: {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Add previous conversation messages if provided
    if (messages && messages.length > 0) {
      messages.forEach((msg, index) => {
        mockSession.messages.push({
          id: `user_msg_${index}`,
          session_id: sessionPathId,
          role: 'user',
          content: msg,
          meta_data: {},
          created_at: new Date(Date.now() - (messages.length - index) * 1000).toISOString(),
        });
        mockSession.messages.push({
          id: `bot_msg_${index}`,
          session_id: sessionPathId,
          role: 'assistant',
          content: `Response to: ${msg}`,
          meta_data: {},
          created_at: new Date(Date.now() - (messages.length - index) * 1000 + 500).toISOString(),
        });
      });
    }

    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockSession)
    });
  });

  // Mock message sending for resumed sessions
  await page.route('**/api/v1/sessions/**/messages', route => {
    const url = route.request().url();
    const sessionId = url.split('/')[4]; // Extract session ID from URL

    const mockResponse = {
      id: `msg_${Date.now()}`,
      session_id: sessionId,
      role: 'assistant',
      content: "Thank you for your message. How can I help you further?",
      meta_data: {},
      created_at: new Date().toISOString(),
    };
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockResponse)
    });
  });
}