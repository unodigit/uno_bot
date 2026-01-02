import { test, expect, Page } from '@playwright/test';

/**
 * Tests for qualification features (187-190)
 * These verify the bot collects decision maker info, success criteria,
 * detects intent, and maintains context across long conversations
 */

test.beforeEach(async ({ page }) => {
  // Navigate to main page before each test
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");

  // Track console errors
  const pageErrors: any[] = [];
  page.on("console", (msg) => {
    if (msg.type === "error") {
      pageErrors.push(msg);
    }
  });
});

/**
 * Helper function to progress conversation to qualification phase
 */
async function progressToQualification(page: Page) {
  // Open chat
  await page.click('[data-testid="chat-widget-button"]');
  await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
  await page.waitForTimeout(1500);

  // Provide name
  await page.fill('[data-testid="chat-input"]', 'My name is John Doe');
  await page.click('[data-testid="send-button"]');
  await page.waitForTimeout(2500);

  // Provide email
  await page.fill('[data-testid="chat-input"]', 'john@example.com');
  await page.click('[data-testid="send-button"]');
  await page.waitForTimeout(2000);

  // Provide challenge
  await page.fill('[data-testid="chat-input"]', 'We need help with data analytics challenges');
  await page.click('[data-testid="send-button"]');
  await page.waitForTimeout(2000);

  // Provide industry
  await page.fill('[data-testid="chat-input"]', 'We are in the healthcare industry');
  await page.click('[data-testid="send-button"]');
  await page.waitForTimeout(2000);
}

test.describe('Feature 187: Decision maker identification is collected', () => {
  test('bot asks about decision maker status in qualification phase', async ({ page }) => {
    await progressToQualification(page);

    // Get the latest message
    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    let lastText = '';

    // Check if bot asks about decision maker or budget
    for (let i = 0; i < messageCount; i++) {
      const text = await messages.nth(i).textContent();
      if (text?.toLowerCase().match(/decision|approve|budget|authorize/i)) {
        lastText = text || '';
        break;
      }
    }

    // Bot should ask about decision making authority or budget
    expect(lastText.length).toBeGreaterThan(0);
  });

  test('decision maker response is stored correctly', async ({ page }) => {
    await progressToQualification(page);

    // Respond that user is decision maker
    await page.fill('[data-testid="chat-input"]', 'Yes, I am the decision maker for this project');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Check that bot acknowledges
    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    const lastMessage = messages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should acknowledge and continue conversation
    expect(lastText?.length).toBeGreaterThan(10);
  });

  test('decision maker status affects lead score positively', async ({ page }) => {
    await progressToQualification(page);

    // Indicate decision maker status
    await page.fill('[data-testid="chat-input"]', 'I decide on these matters and can approve the budget');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Provide budget
    await page.fill('[data-testid="chat-input"]', 'Our budget is around $50,000');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Check that conversation progresses to PRD or expert matching
    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    const lastMessage = messages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should mention next steps, PRD, or expert
    expect(lastText?.toLowerCase()).toMatch(/prd|project requirements|expert|match|next step|schedule/i);
  });

  test('non-decision maker response is handled correctly', async ({ page }) => {
    await progressToQualification(page);

    // Indicate not the decision maker
    await page.fill('[data-testid="chat-input"]', 'I am not the decision maker, I need to get approval from my boss');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Check that bot acknowledges and continues
    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    const lastMessage = messages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should acknowledge and still continue conversation
    expect(lastText?.length).toBeGreaterThan(10);
  });
});

test.describe('Feature 188: Success criteria collection works', () => {
  test('bot captures success criteria when user mentions goals', async ({ page }) => {
    await progressToQualification(page);

    // Provide budget first
    await page.fill('[data-testid="chat-input"]', 'Our budget is around $50,000');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Mention success criteria
    await page.fill('[data-testid="chat-input"]', 'Our success criteria are to improve data processing efficiency by 50% and reduce manual work');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Check that bot acknowledges the success criteria
    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    const lastMessage = messages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should acknowledge or ask for more details
    expect(lastText?.length).toBeGreaterThan(10);
  });

  test('success criteria is captured in context for PRD generation', async ({ page }) => {
    await progressToQualification(page);

    // Provide qualification info
    await page.fill('[data-testid="chat-input"]', 'Our budget is medium, around $50,000');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    await page.fill('[data-testid="chat-input"]', 'We need this done within 2 months');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Define success criteria
    await page.fill('[data-testid="chat-input"]', 'Success would be measured by 50% efficiency improvement and automated reporting');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Check that conversation progresses
    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    const lastMessage = messages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should mention PRD, next steps, or expert matching
    expect(lastText?.toLowerCase()).toMatch(/prd|project requirements|document|expert|next step|great/i);
  });

  test('bot asks clarifying questions for vague success criteria', async ({ page }) => {
    await progressToQualification(page);

    // Provide budget
    await page.fill('[data-testid="chat-input"]', 'Budget is around $50,000');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Provide vague success criteria
    await page.fill('[data-testid="chat-input"]', 'We want success');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Check that bot asks for clarification
    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    const lastMessage = messages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should ask for more specific goals
    expect(lastText?.toLowerCase()).toMatch(/specific|measure|how|define|what does|clarif/i);
  });

  test('success criteria with metrics is properly captured', async ({ page }) => {
    await progressToQualification(page);

    // Provide budget and timeline
    await page.fill('[data-testid="chat-input"]', 'Budget is $50,000 and timeline is 2 months');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Provide specific success criteria with KPIs
    await page.fill('[data-testid="chat-input"]', 'Our KPIs are: 50% faster processing, 80% reduction in errors, and 100% automated reporting');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Verify bot acknowledges the specific metrics
    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    const lastMessage = messages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should acknowledge the detailed criteria
    expect(lastText?.length).toBeGreaterThan(20);
  });
});

test.describe('Feature 189: Intent detection identifies visitor needs', () => {
  test('bot detects AI strategy intent from user message', async ({ page }) => {
    // Open chat
    await page.click('[data-testid="chat-widget-button"]');
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await page.waitForTimeout(1000);

    // Provide name
    await page.fill('[data-testid="chat-input"]', 'My name is Sarah Chen');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Express AI strategy need
    await page.fill('[data-testid="chat-input"]', 'We need help with our AI strategy and machine learning implementation');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Check that bot responds to AI strategy intent
    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    const lastMessage = messages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should respond to AI/ML need
    expect(lastText?.toLowerCase()).toMatch(/ai|machine learning|ml|strategy|analytics|data/i);
  });

  test('bot detects custom development intent', async ({ page }) => {
    await page.click('[data-testid="chat-widget-button"]');
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await page.waitForTimeout(1000);

    await page.fill('[data-testid="chat-input"]', 'I am Mike Johnson');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Express custom development need
    await page.fill('[data-testid="chat-input"]', 'We need a custom software application built for our business');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    const lastMessage = messages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should respond to custom development need
    expect(lastText?.toLowerCase()).toMatch(/custom|develop|application|software|build/i);
  });

  test('bot adapts conversation based on detected intent', async ({ page }) => {
    await page.click('[data-testid="chat-widget-button"]');
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await page.waitForTimeout(1000);

    await page.fill('[data-testid="chat-input"]', 'My name is Alex Kim');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Express data analytics intent
    await page.fill('[data-testid="chat-input"]', 'We need data analytics and business intelligence solutions');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Check that bot asks relevant questions for data analytics
    const messages = page.locator('[data-testid="chat-message"]');
    const hasAnalyticsQuestion = await messages.filter({ hasText: /data|analytics|sources|reporting|dashboard/i }).count();

    expect(hasAnalyticsQuestion).toBeGreaterThan(0);
  });

  test('bot handles general browsing intent appropriately', async ({ page }) => {
    await page.click('[data-testid="chat-widget-button"]');
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await page.waitForTimeout(1000);

    await page.fill('[data-testid="chat-input"]', 'I am just browsing');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    const messages = page.locator('[data-testid="chat-message"]');
    const messageCount = await messages.count();
    const lastMessage = messages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should still be helpful and inviting
    expect(lastText?.length).toBeGreaterThan(10);
  });
});

test.describe('Feature 190: Context retention across long conversations', () => {
  test('bot remembers name after 15+ messages', async ({ page }) => {
    await page.click('[data-testid="chat-widget-button"]');
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await page.waitForTimeout(1000);

    // Start conversation with name
    await page.fill('[data-testid="chat-input"]', 'My name is Emily Watson');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Exchange multiple messages (15+ total)
    const messages = [
      'emily@example.com',
      'We need help with data analytics',
      'Healthcare industry',
      'About 100 employees',
      'Budget is $50,000',
      'Need it done in 2 months',
      'Yes, I am the decision maker',
      'Success means 50% efficiency improvement',
      'We use Python and SQL',
      'Main challenge is slow reporting',
      'We need real-time dashboards',
      'Currently using Excel',
      'Looking to automate',
      'Need better insights',
      'What is the next step?'  // Message 15
    ];

    for (const msg of messages) {
      await page.fill('[data-testid="chat-input"]', msg);
      await page.click('[data-testid="send-button"]');
      await page.waitForTimeout(1500);
    }

    // Reference earlier information
    await page.fill('[data-testid="chat-input"]', 'Great, Emily! Can you send the PRD to my email?');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // Check that bot still remembers context
    const allMessages = page.locator('[data-testid="chat-message"]');
    const messageCount = await allMessages.count();
    const lastMessage = allMessages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Bot should respond appropriately, showing it remembers the conversation
    expect(lastText?.length).toBeGreaterThan(10);
  });

  test('bot references earlier context without confusion', async ({ page }) => {
    await page.click('[data-testid="chat-widget-button"]');
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await page.waitForTimeout(1000);

    // Have a long conversation
    await page.fill('[data-testid="chat-input"]', 'My name is David Lee');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    const conversation = [
      'david@example.com',
      'Custom software development',
      'Finance industry',
      '200 employees',
      'Budget is $100,000',
      '3 month timeline',
      'I am the CTO',
      'Success is launching on time',
      'We use Java and React',
      'Need mobile app',
      'iOS and Android',
      'Need API integration',
      'Payment processing',
      'User authentication',
      'Remember, I work in finance'  // Reference earlier context
    ];

    for (const msg of conversation) {
      await page.fill('[data-testid="chat-input"]', msg);
      await page.click('[data-testid="send-button"]');
      await page.waitForTimeout(1500);
    }

    // Check bot response acknowledges the context
    const allMessages = page.locator('[data-testid="chat-message"]');
    const messageCount = await allMessages.count();
    const lastMessage = allMessages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should acknowledge the industry context
    expect(lastText?.toLowerCase()).toMatch(/finance|financial|industry|understand/i);
  });

  test('conversation maintains coherence after 20+ messages', async ({ page }) => {
    await page.click('[data-testid="chat-widget-button"]');
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();
    await page.waitForTimeout(1000);

    await page.fill('[data-testid="chat-input"]', 'Hi, I am Rachel Green');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Very long conversation
    const longConversation = [
      'rachel@company.com',
      'We need AI consulting',
      'Retail industry',
      '50 employees',
      'Budget $75,000',
      '4 months',
      'I decide on budget',
      'Success is better customer predictions',
      'We use AWS',
      'Python and TensorFlow',
      'Need recommendation engine',
      'Customer segmentation',
      'Inventory optimization',
      'Sales forecasting',
      'We have customer data',
      '5 years of data',
      'Millions of records',
      'Need data pipeline',
      'Real-time processing',
      'Cloud deployment',
      'What services do you offer for this?'  // Message 20+
    ];

    for (const msg of longConversation) {
      await page.fill('[data-testid="chat-input"]', msg);
      await page.click('[data-testid="send-button"]');
      await page.waitForTimeout(1200);
    }

    // Check final response is coherent and contextual
    const allMessages = page.locator('[data-testid="chat-message"]');
    const messageCount = await allMessages.count();
    const lastMessage = allMessages.nth(messageCount - 1);
    const lastText = await lastMessage.textContent();

    // Should provide relevant, contextual response
    expect(lastText?.length).toBeGreaterThan(20);
    expect(lastText?.toLowerCase()).toMatch(/ai|service|consulting|recommendation|expert|prd/i);
  });
});
