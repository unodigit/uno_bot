"""E2E tests for session resume via email link functionality."""

import pytest
from playwright.async_api import Page, expect
import asyncio


@pytest.mark.asyncio
async def test_session_resume_via_email_link(page: Page):
    """Test that session can be resumed via email link with session_id parameter."""

    print("\n=== Test: Session Resume via Email Link ===")

    # Step 1: Start conversation and get session ID
    print("Step 1: Starting conversation and getting session ID")
    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")

    # Open chat widget
    chat_button = page.get_by_test_id("chat-widget-button")
    await chat_button.click()

    # Wait for chat to open and initial message
    await page.wait_for_selector('[data-testid="messages-container"]')
    await expect(page.locator('[data-testid="messages-container"]')).to_be_visible()

    # Get session ID from localStorage
    session_id = await page.evaluate("localStorage.getItem('unobot_session_id')")
    assert session_id is not None, "Session should be created automatically"
    print(f"✓ Created session ID: {session_id}")

    # Step 2: Exchange a few messages to establish conversation
    print("Step 2: Exchanging messages to establish conversation")
    message_input = page.get_by_placeholder("Type your message...")
    await message_input.fill("Hi, I need help with a business consultation.")
    await message_input.press("Enter")

    # Wait for bot response
    await page.wait_for_timeout(3000)  # Wait for streaming response

    # Send another message
    await message_input.fill("Can you tell me about your services?")
    await message_input.press("Enter")

    await page.wait_for_timeout(3000)  # Wait for response

    # Step 3: Get session resume URL
    print("Step 3: Getting session resume URL")
    resume_url = await page.evaluate(f"window.location.origin + '?session_id={session_id}'")
    print(f"✓ Session resume URL: {resume_url}")

    # Step 4: Close browser completely (simulate user closing browser)
    print("Step 4: Closing browser to simulate user action")
    await page.close()

    # Create new page to simulate fresh browser session
    new_page = await page.context.browser.new_page()

    # Step 5: Open email link with session ID
    print("Step 5: Opening email link with session ID")
    await new_page.goto(resume_url)
    await new_page.wait_for_load_state("networkidle")

    # Step 6: Verify conversation is resumed
    print("Step 6: Verifying conversation is resumed")
    new_session_id = await new_page.evaluate("localStorage.getItem('unobot_session_id')")
    assert new_session_id == session_id, f"Session ID should be the same. Expected: {session_id}, Got: {new_session_id}"

    # Step 7: Verify full history is visible
    print("Step 7: Verifying full conversation history is visible")
    await new_page.wait_for_selector('[data-testid="chat-widget-button"]')
    chat_button = new_page.get_by_test_id("chat-widget-button")
    await chat_button.click()

    # Wait for chat to open
    await new_page.wait_for_selector('[data-testid="messages-container"]')
    await expect(new_page.locator('[data-testid="messages-container"]')).to_be_visible()

    # Check that messages are present (should have more than just the welcome message)
    message_elements = await new_page.locator('[data-testid="messages-container"] .bg-white').all()
    print(f"✓ Found {len(message_elements)} message elements in resumed session")

    # Verify one of our messages is present
    if len(message_elements) > 0:
        message_text = await message_elements[-1].inner_text()
        print(f"✓ Last message content: {message_text}")
        assert "business consultation" in message_text.lower() or "services" in message_text.lower() or "hello" in message_text.lower(), \
            f"Should contain user message content: {message_text}"

    await new_page.close()


@pytest.mark.asyncio
async def test_session_resume_preserves_conversation_history(page: Page):
    """Test that full conversation history is preserved when resuming via email link."""

    print("\n=== Test: Conversation History Preservation ===")

    # Step 1: Create a comprehensive conversation
    print("Step 1: Creating comprehensive conversation")
    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")

    # Open chat
    chat_button = page.get_by_test_id("chat-widget-button")
    await chat_button.click()
    await page.wait_for_selector('[data-testid="messages-container"]')

    # Get initial session ID
    session_id = await page.evaluate("localStorage.getItem('unobot_session_id')")
    print(f"✓ Initial session ID: {session_id}")

    # Exchange multiple messages
    messages_to_send = [
        "Hello, I'm interested in AI consulting services",
        "Can you help me with digital transformation?",
        "What's your experience in healthcare AI?",
        "How much would a project like this cost?"
    ]

    message_input = page.get_by_placeholder("Type your message...")

    for i, message in enumerate(messages_to_send):
        print(f"Step 1.{i+1}: Sending message {i+1}: {message}")
        await message_input.fill(message)
        await message_input.press("Enter")
        await page.wait_for_timeout(3000)  # Wait for response

    # Record the conversation state
    initial_messages = await page.locator('[data-testid="messages-container"] .bg-white').all()
    initial_message_count = len(initial_messages)
    print(f"✓ Initial conversation has {initial_message_count} messages")

    # Get a sample user message to verify later
    sample_user_message = messages_to_send[1]
    print(f"✓ Sample user message to verify: '{sample_user_message}'")

    # Step 2: Get resume URL and simulate email click
    print("Step 2: Getting resume URL")
    resume_url = await page.evaluate(f"window.location.origin + '?session_id={session_id}'")
    print(f"✓ Resume URL: {resume_url}")

    # Close and create new page
    await page.close()
    new_page = await page.context.browser.new_page()

    # Step 3: Resume session via email link
    print("Step 3: Resuming session via email link")
    await new_page.goto(resume_url)
    await new_page.wait_for_load_state("networkidle")

    # Verify session ID is preserved
    resumed_session_id = await new_page.evaluate("localStorage.getItem('unobot_session_id')")
    assert resumed_session_id == session_id, "Session ID should be preserved"

    # Step 4: Verify conversation history is intact
    print("Step 4: Verifying conversation history preservation")
    chat_button = new_page.get_by_test_id("chat-widget-button")
    await chat_button.click()
    await new_page.wait_for_selector('[data-testid="messages-container"]')

    # Check message count
    resumed_messages = await new_page.locator('[data-testid="messages-container"] .bg-white').all()
    resumed_message_count = len(resumed_messages)
    print(f"✓ Resumed session has {resumed_message_count} messages")

    # Verify message count is preserved
    assert resumed_message_count == initial_message_count, \
        f"Message count should be preserved. Initial: {initial_message_count}, Resumed: {resumed_message_count}"

    # Verify specific user message content
    message_found = False
    for msg_element in resumed_messages:
        msg_text = await msg_element.inner_text()
        if sample_user_message.lower() in msg_text.lower():
            message_found = True
            print(f"✓ Found sample message in resumed session: '{sample_user_message}'")
            break

    assert message_found, f"Sample user message should be preserved in resumed session: '{sample_user_message}'"

    # Verify bot responses are also preserved
    bot_responses_found = 0
    for msg_element in resumed_messages:
        msg_text = await msg_element.inner_text()
        # Bot messages typically start with emojis or have AI-like content
        if any(indicator in msg_text for indicator in ["Hello", "I'm UnoBot", "Welcome", "Based", "Here"]):
            bot_responses_found += 1

    print(f"✓ Found {bot_responses_found} bot responses in resumed session")
    assert bot_responses_found > 0, "Bot responses should be preserved in resumed session"

    await new_page.close()


@pytest.mark.asyncio
async def test_session_resume_preserves_session_context(page: Page):
    """Test that session context (phase, client info, business context) is preserved."""

    print("\n=== Test: Session Context Preservation ===")

    # Step 1: Create conversation and gather context
    print("Step 1: Creating conversation with context")
    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")

    chat_button = page.get_by_test_id("chat-widget-button")
    await chat_button.click()
    await page.wait_for_selector('[data-testid="messages-container"]')

    session_id = await page.evaluate("localStorage.getItem('unobot_session_id')")
    print(f"✓ Session ID: {session_id}")

    # Send messages to establish context
    context_messages = [
        "My name is John Smith",
        "I work at Acme Corp in the healthcare industry",
        "We need help with AI-driven patient analytics"
    ]

    message_input = page.get_by_placeholder("Type your message...")

    for message in context_messages:
        await message_input.fill(message)
        await message_input.press("Enter")
        await page.wait_for_timeout(3000)

    # Get session context from store
    session_context = await page.evaluate("""
        (async () => {
            // Access the Zustand store
            const store = window.__ZUSTAND_STORE__;
            if (store) {
                return {
                    currentPhase: store.getState().currentPhase,
                    clientInfo: store.getState().clientInfo,
                    businessContext: store.getState().businessContext,
                    messages: store.getState().messages.length
                };
            }
            return null;
        })()
    """)

    if session_context:
        print(f"✓ Session context captured:")
        print(f"  - Current Phase: {session_context['currentPhase']}")
        print(f"  - Client Info: {session_context['clientInfo']}")
        print(f"  - Business Context: {session_context['businessContext']}")
        print(f"  - Message Count: {session_context['messages']}")
    else:
        print("⚠️ Could not access session context directly, will test via UI")

    # Step 2: Resume session
    print("Step 2: Resuming session")
    resume_url = await page.evaluate(f"window.location.origin + '?session_id={session_id}'")
    await page.close()
    new_page = await page.context.browser.new_page()
    await new_page.goto(resume_url)
    await new_page.wait_for_load_state("networkidle")

    # Step 3: Verify context preservation
    print("Step 3: Verifying context preservation")
    resumed_session_id = await new_page.evaluate("localStorage.getItem('unobot_session_id')")
    assert resumed_session_id == session_id, "Session ID should be preserved"

    # Check if client name appears in conversation
    chat_button = new_page.get_by_test_id("chat-widget-button")
    await chat_button.click()
    await new_page.wait_for_selector('[data-testid="messages-container"]')

    messages = await new_page.locator('[data-testid="messages-container"] .bg-white').all()
    client_name_found = False

    for msg_element in messages:
        msg_text = await msg_element.inner_text()
        if "John Smith" in msg_text or "john" in msg_text.lower():
            client_name_found = True
            print(f"✓ Client name found in resumed session: 'John Smith'")
            break

    assert client_name_found, "Client information should be preserved in resumed session"

    # Verify business context is preserved
    business_context_found = False
    for msg_element in messages:
        msg_text = await msg_element.inner_text()
        if "healthcare" in msg_text.lower() or "patient analytics" in msg_text.lower():
            business_context_found = True
            print(f"✓ Business context found in resumed session")
            break

    assert business_context_found, "Business context should be preserved in resumed session"

    await new_page.close()


@pytest.mark.asyncio
async def test_session_resume_with_empty_conversation(page: Page):
    """Test resuming a session that has minimal conversation history."""

    print("\n=== Test: Resume Session with Minimal History ===")

    # Step 1: Create session with just welcome message
    print("Step 1: Creating session with minimal history")
    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")

    chat_button = page.get_by_test_id("chat-widget-button")
    await chat_button.click()
    await page.wait_for_selector('[data-testid="messages-container"]')

    session_id = await page.evaluate("localStorage.getItem('unobot_session_id')")
    print(f"✓ Session ID: {session_id}")

    # Wait for welcome message to load
    await page.wait_for_timeout(2000)

    # Get initial message count
    initial_messages = await page.locator('[data-testid="messages-container"] .bg-white').all()
    initial_count = len(initial_messages)
    print(f"✓ Initial message count: {initial_count}")

    # Step 2: Resume session
    print("Step 2: Resuming session")
    resume_url = await page.evaluate(f"window.location.origin + '?session_id={session_id}'")
    await page.close()
    new_page = await page.context.browser.new_page()
    await new_page.goto(resume_url)
    await new_page.wait_for_load_state("networkidle")

    # Step 3: Verify minimal history is preserved
    print("Step 3: Verifying minimal history preservation")
    resumed_session_id = await new_page.evaluate("localStorage.getItem('unobot_session_id')")
    assert resumed_session_id == session_id, "Session ID should be preserved"

    chat_button = new_page.get_by_test_id("chat-widget-button")
    await chat_button.click()
    await new_page.wait_for_selector('[data-testid="messages-container"]')

    resumed_messages = await new_page.locator('[data-testid="messages-container"] .bg-white').all()
    resumed_count = len(resumed_messages)
    print(f"✓ Resumed message count: {resumed_count}")

    assert resumed_count == initial_count, \
        f"Message count should be preserved. Initial: {initial_count}, Resumed: {resumed_count}"

    # Verify welcome message is present
    welcome_found = False
    for msg_element in resumed_messages:
        msg_text = await msg_element.inner_text()
        if "Welcome" in msg_text or "UnoBot" in msg_text:
            welcome_found = True
            print(f"✓ Welcome message found in resumed session")
            break

    assert welcome_found, "Welcome message should be preserved in resumed session"

    await new_page.close()


@pytest.mark.asyncio
async def test_session_resume_url_generation(page: Page):
    """Test that session resume URLs are generated correctly."""

    print("\n=== Test: Session Resume URL Generation ===")

    # Step 1: Create session and generate URL
    print("Step 1: Creating session and generating resume URL")
    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")

    chat_button = page.get_by_test_id("chat-widget-button")
    await chat_button.click()
    await page.wait_for_selector('[data-testid="messages-container"]')

    session_id = await page.evaluate("localStorage.getItem('unobot_session_id')")
    print(f"✓ Session ID: {session_id}")

    # Generate resume URL using the store method
    resume_url = await page.evaluate("""
        (async () => {
            const store = window.__ZUSTAND_STORE__;
            if (store && store.getState().generateSessionResumeUrl) {
                return store.getState().generateSessionResumeUrl();
            }
            // Fallback to manual generation
            return window.location.origin + '?session_id=' + localStorage.getItem('unobot_session_id');
        })()
    """)

    print(f"✓ Generated resume URL: {resume_url}")

    # Step 2: Verify URL format
    print("Step 2: Verifying URL format")
    assert resume_url is not None, "Resume URL should be generated"
    assert 'session_id=' in resume_url, "URL should contain session_id parameter"
    assert session_id in resume_url, "URL should contain the actual session ID"

    # Check that URL uses current origin
    current_origin = await page.evaluate("window.location.origin")
    assert current_origin in resume_url, "URL should use current origin"

    # Step 3: Test URL functionality
    print("Step 3: Testing URL functionality")
    await page.close()
    new_page = await page.context.browser.new_page()
    await new_page.goto(resume_url)
    await new_page.wait_for_load_state("networkidle")

    # Verify session is resumed
    resumed_session_id = await new_page.evaluate("localStorage.getItem('unobot_session_id')")
    assert resumed_session_id == session_id, "Session should be resumed via generated URL"

    await new_page.close()


@pytest.mark.asyncio
async def test_session_resume_multiple_times(page: Page):
    """Test that a session can be resumed multiple times via email links."""

    print("\n=== Test: Multiple Session Resumes ===")

    # Step 1: Create initial session
    print("Step 1: Creating initial session")
    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")

    chat_button = page.get_by_test_id("chat-widget-button")
    await chat_button.click()
    await page.wait_for_selector('[data-testid="messages-container"]')

    session_id = await page.evaluate("localStorage.getItem('unobot_session_id')")
    print(f"✓ Session ID: {session_id}")

    # Add some conversation
    message_input = page.get_by_placeholder("Type your message...")
    await message_input.fill("This is test message for multiple resume")
    await message_input.press("Enter")
    await page.wait_for_timeout(3000)

    initial_messages = await page.locator('[data-testid="messages-container"] .bg-white').all()
    initial_count = len(initial_messages)
    print(f"✓ Initial message count: {initial_count}")

    # Get resume URL
    resume_url = await page.evaluate(f"window.location.origin + '?session_id={session_id}'")
    print(f"✓ Resume URL: {resume_url}")

    # Step 2: First resume
    print("Step 2: First resume")
    await page.close()
    page1 = await page.context.browser.new_page()
    await page1.goto(resume_url)
    await page1.wait_for_load_state("networkidle")

    resumed_session_id = await page1.evaluate("localStorage.getItem('unobot_session_id')")
    assert resumed_session_id == session_id, "First resume should work"

    # Step 3: Second resume
    print("Step 3: Second resume")
    await page1.close()
    page2 = await page.context.browser.new_page()
    await page2.goto(resume_url)
    await page2.wait_for_load_state("networkidle")

    resumed_session_id_2 = await page2.evaluate("localStorage.getItem('unobot_session_id')")
    assert resumed_session_id_2 == session_id, "Second resume should work"

    # Step 4: Third resume
    print("Step 4: Third resume")
    await page2.close()
    page3 = await page.context.browser.new_page()
    await page3.goto(resume_url)
    await page3.wait_for_load_state("networkidle")

    resumed_session_id_3 = await page3.evaluate("localStorage.getItem('unobot_session_id')")
    assert resumed_session_id_3 == session_id, "Third resume should work"

    # Step 5: Verify conversation history is consistent across resumes
    print("Step 5: Verifying conversation history consistency")
    for i, test_page in enumerate([page1, page2, page3], 1):
        if test_page.is_closed:
            test_page = await page.context.browser.new_page()
            await test_page.goto(resume_url)
            await test_page.wait_for_load_state("networkidle")

        chat_button = test_page.get_by_test_id("chat-widget-button")
        await chat_button.click()
        await test_page.wait_for_selector('[data-testid="messages-container"]')

        messages = await test_page.locator('[data-testid="messages-container"] .bg-white').all()
        message_count = len(messages)
        print(f"✓ Resume {i}: {message_count} messages")

        assert message_count == initial_count, \
            f"Resume {i} should have same message count as initial. Initial: {initial_count}, Resume {i}: {message_count}"

        # Check for the test message
        test_message_found = False
        for msg_element in messages:
            msg_text = await msg_element.inner_text()
            if "test message for multiple resume" in msg_text:
                test_message_found = True
                break

        assert test_message_found, f"Test message should be present in resume {i}"

        if not test_page.is_closed:
            await test_page.close()

    print("✓ All multiple resume tests passed")


@pytest.mark.asyncio
async def test_session_resume_chat_widget_behavior(page: Page):
    """Test that chat widget behavior is correct after session resume."""

    print("\n=== Test: Chat Widget Behavior After Resume ===")

    # Step 1: Create session and close chat
    print("Step 1: Creating session and closing chat")
    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")

    chat_button = page.get_by_test_id("chat-widget-button")
    await chat_button.click()
    await page.wait_for_selector('[data-testid="messages-container"]')

    session_id = await page.evaluate("localStorage.getItem('unobot_session_id')")
    print(f"✓ Session ID: {session_id}")

    # Send a message
    message_input = page.get_by_placeholder("Type your message...")
    await message_input.fill("Testing chat widget behavior")
    await message_input.press("Enter")
    await page.wait_for_timeout(3000)

    # Close chat window
    close_button = page.get_by_test_id("close-button")
    await close_button.click()
    await page.wait_for_timeout(1000)

    # Step 2: Resume session
    print("Step 2: Resuming session")
    resume_url = await page.evaluate(f"window.location.origin + '?session_id={session_id}'")
    await page.close()
    new_page = await page.context.browser.new_page()
    await new_page.goto(resume_url)
    await new_page.wait_for_load_state("networkidle")

    # Step 3: Test chat widget behavior
    print("Step 3: Testing chat widget behavior")

    # Verify session ID is preserved
    resumed_session_id = await new_page.evaluate("localStorage.getItem('unobot_session_id')")
    assert resumed_session_id == session_id, "Session should be resumed"

    # Test 1: Chat widget should be closed initially
    chat_window = new_page.locator('[data-testid="chat-window"]')
    is_open = await chat_window.is_visible()
    assert not is_open, "Chat window should be closed initially after resume"

    # Test 2: Clicking chat button should open existing session
    chat_button = new_page.get_by_test_id("chat-widget-button")
    await chat_button.click()
    await new_page.wait_for_selector('[data-testid="chat-window"]')
    await expect(new_page.locator('[data-testid="chat-window"]')).to_be_visible()

    # Test 3: Conversation should be visible
    messages_container = new_page.locator('[data-testid="messages-container"]')
    await expect(messages_container).to_be_visible()

    messages = await new_page.locator('[data-testid="messages-container"] .bg-white').all()
    assert len(messages) > 0, "Messages should be visible after opening chat"

    # Test 4: Should be able to send new messages
    message_input = new_page.get_by_placeholder("Type your message...")
    test_message = "Testing new message after resume"
    await message_input.fill(test_message)
    await message_input.press("Enter")
    await new_page.wait_for_timeout(3000)

    # Verify new message was sent
    new_messages = await new_page.locator('[data-testid="messages-container"] .bg-white').all()
    new_message_found = False
    for msg_element in new_messages:
        msg_text = await msg_element.inner_text()
        if test_message in msg_text:
            new_message_found = True
            break

    assert new_message_found, "New message should be sent after resume"

    await new_page.close()


@pytest.mark.asyncio
async def test_session_resume_url_parameter_handling(page: Page):
    """Test that session ID in URL parameter is properly handled."""

    # Create a test session ID
    test_session_id = "test-session-123"

    # Navigate to URL with session_id parameter
    test_url = f"http://localhost:5173?session_id={test_session_id}"
    await page.goto(test_url)
    await page.wait_for_load_state("networkidle")

    # Verify session ID is stored in localStorage
    stored_session_id = await page.evaluate("localStorage.getItem('unobot_session_id')")
    assert stored_session_id == test_session_id, \
        f"Expected {test_session_id}, got {stored_session_id}"

    print(f"Successfully stored session ID: {stored_session_id}")


@pytest.mark.asyncio
async def test_session_resume_without_parameter(page: Page):
    """Test that normal session creation works when no session_id parameter is provided."""

    # Navigate to root URL without session_id parameter
    await page.goto("http://localhost:5173")
    await page.wait_for_load_state("networkidle")

    # Session ID should be null initially
    initial_session_id = await page.evaluate("localStorage.getItem('unobot_session_id')")
    assert initial_session_id is None, "No session should exist initially"

    # Open chat to create new session
    chat_button = page.get_by_test_id("chat-widget-button")
    await chat_button.click()

    # Wait for session to be created
    await page.wait_for_timeout(1000)

    # Now session should be created
    created_session_id = await page.evaluate("localStorage.getItem('unobot_session_id')")
    assert created_session_id is not None, "Session should be created when chat is opened"

    print(f"New session created: {created_session_id}")