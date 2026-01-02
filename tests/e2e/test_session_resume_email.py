"""E2E tests for session resume via email link functionality."""
from playwright.sync_api import Page, expect


FRONTEND_URL = "http://localhost:5173"


class TestSessionResumeEmail:
    """Test cases for session resume via email link functionality."""

    def test_session_resume_via_email_link(self, page: Page):
        """
        Test: Session can be resumed via email link with session_id parameter

        Steps:
        1. Start conversation and get session ID
        2. Exchange messages to establish conversation
        3. Get session resume URL
        4. Close browser (simulate user action)
        5. Open email link with session ID
        6. Verify conversation is resumed
        7. Verify full history is visible
        """
        print("\n=== Test: Session Resume via Email Link ===")

        # Step 1: Start conversation and get session ID
        print("Step 1: Starting conversation and getting session ID")
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat to open and initial message
        page.wait_for_selector('[data-testid="messages-container"]')
        expect(page.locator('[data-testid="messages-container"]')).to_be_visible()

        # Get session ID from localStorage
        session_id = page.evaluate("localStorage.getItem('unobot_session_id')")
        assert session_id is not None, "Session should be created automatically"
        print(f"✓ Created session ID: {session_id}")

        # Step 2: Exchange a few messages to establish conversation
        print("Step 2: Exchanging messages to establish conversation")
        message_input = page.get_by_placeholder("Type your message...")
        message_input.fill("Hi, I need help with a business consultation.")
        message_input.press("Enter")

        # Wait for bot response
        page.wait_for_timeout(3000)  # Wait for streaming response

        # Send another message
        message_input.fill("Can you tell me about your services?")
        message_input.press("Enter")

        page.wait_for_timeout(3000)  # Wait for response

        # Step 3: Get session resume URL
        print("Step 3: Getting session resume URL")
        resume_url = page.evaluate(f"window.location.origin + '?session_id={session_id}'")
        print(f"✓ Session resume URL: {resume_url}")

        # Step 4: Close browser completely (simulate user closing browser)
        print("Step 4: Closing browser to simulate user action")
        context = page.context
        page.close()

        # Create new page to simulate fresh browser session
        new_page = context.new_page()

        # Step 5: Open email link with session ID
        print("Step 5: Opening email link with session ID")
        new_page.goto(resume_url)
        new_page.wait_for_load_state("networkidle")

        # Step 6: Verify conversation is resumed
        print("Step 6: Verifying conversation is resumed")
        new_session_id = new_page.evaluate("localStorage.getItem('unobot_session_id')")
        assert new_session_id == session_id, f"Session ID should be the same. Expected: {session_id}, Got: {new_session_id}"

        # Step 7: Verify full history is visible
        print("Step 7: Verifying full conversation history is visible")
        new_page.wait_for_selector('[data-testid="chat-widget-button"]')
        chat_button = new_page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for chat to open
        new_page.wait_for_selector('[data-testid="messages-container"]')
        expect(new_page.locator('[data-testid="messages-container"]')).to_be_visible()

        # Check that messages are present (should have more than just the welcome message)
        message_elements = new_page.locator('[data-testid="messages-container"] .bg-white').all()
        print(f"✓ Found {len(message_elements)} message elements in resumed session")

        # Verify one of our messages is present
        if len(message_elements) > 0:
            message_text = message_elements[-1].inner_text()
            print(f"✓ Last message content: {message_text}")
            assert "business consultation" in message_text.lower() or "services" in message_text.lower() or "hello" in message_text.lower(), \
                f"Should contain user message content: {message_text}"

        new_page.close()

    def test_session_resume_preserves_conversation_history(self, page: Page):
        """
        Test: Full conversation history is preserved when resuming via email link

        Steps:
        1. Create a comprehensive conversation
        2. Get resume URL and simulate email click
        3. Resume session via email link
        4. Verify conversation history is intact
        """
        print("\n=== Test: Conversation History Preservation ===")

        # Step 1: Create a comprehensive conversation
        print("Step 1: Creating comprehensive conversation")
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Open chat
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        page.wait_for_selector('[data-testid="messages-container"]')

        # Get initial session ID
        session_id = page.evaluate("localStorage.getItem('unobot_session_id')")
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
            message_input.fill(message)
            message_input.press("Enter")
            page.wait_for_timeout(3000)  # Wait for response

        # Record the conversation state
        initial_messages = page.locator('[data-testid="messages-container"] .bg-white').all()
        initial_message_count = len(initial_messages)
        print(f"✓ Initial conversation has {initial_message_count} messages")

        # Get a sample user message to verify later
        sample_user_message = messages_to_send[1]
        print(f"✓ Sample user message to verify: '{sample_user_message}'")

        # Step 2: Get resume URL and simulate email click
        print("Step 2: Getting resume URL")
        resume_url = page.evaluate(f"window.location.origin + '?session_id={session_id}'")
        print(f"✓ Resume URL: {resume_url}")

        # Close and create new page
        context = page.context
        page.close()
        new_page = context.new_page()

        # Step 3: Resume session via email link
        print("Step 3: Resuming session via email link")
        new_page.goto(resume_url)
        new_page.wait_for_load_state("networkidle")

        # Verify session ID is preserved
        resumed_session_id = new_page.evaluate("localStorage.getItem('unobot_session_id')")
        assert resumed_session_id == session_id, "Session ID should be preserved"

        # Step 4: Verify conversation history is intact
        print("Step 4: Verifying conversation history preservation")
        chat_button = new_page.get_by_test_id("chat-widget-button")
        chat_button.click()
        new_page.wait_for_selector('[data-testid="messages-container"]')

        # Check message count
        resumed_messages = new_page.locator('[data-testid="messages-container"] .bg-white').all()
        resumed_message_count = len(resumed_messages)
        print(f"✓ Resumed session has {resumed_message_count} messages")

        # Verify message count is preserved
        assert resumed_message_count == initial_message_count, \
            f"Message count should be preserved. Initial: {initial_message_count}, Resumed: {resumed_message_count}"

        # Verify specific user message content
        message_found = False
        for msg_element in resumed_messages:
            msg_text = msg_element.inner_text()
            if sample_user_message.lower() in msg_text.lower():
                message_found = True
                print(f"✓ Found sample message in resumed session: '{sample_user_message}'")
                break

        assert message_found, f"Sample user message should be preserved in resumed session: '{sample_user_message}'"

        # Verify bot responses are also preserved
        bot_responses_found = 0
        for msg_element in resumed_messages:
            msg_text = msg_element.inner_text()
            # Bot messages typically start with emojis or have AI-like content
            if any(indicator in msg_text for indicator in ["Hello", "I'm UnoBot", "Welcome", "Based", "Here"]):
                bot_responses_found += 1

        print(f"✓ Found {bot_responses_found} bot responses in resumed session")
        assert bot_responses_found > 0, "Bot responses should be preserved in resumed session"

        new_page.close()

    def test_session_resume_preserves_session_context(self, page: Page):
        """
        Test: Session context (phase, client info, business context) is preserved

        Steps:
        1. Create conversation and gather context
        2. Resume session
        3. Verify context preservation
        """
        print("\n=== Test: Session Context Preservation ===")

        # Step 1: Create conversation and gather context
        print("Step 1: Creating conversation with context")
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        page.wait_for_selector('[data-testid="messages-container"]')

        session_id = page.evaluate("localStorage.getItem('unobot_session_id')")
        print(f"✓ Session ID: {session_id}")

        # Send messages to establish context
        context_messages = [
            "My name is John Smith",
            "I work at Acme Corp in the healthcare industry",
            "We need help with AI-driven patient analytics"
        ]

        message_input = page.get_by_placeholder("Type your message...")

        for message in context_messages:
            message_input.fill(message)
            message_input.press("Enter")
            page.wait_for_timeout(3000)

        # Step 2: Resume session
        print("Step 2: Resuming session")
        resume_url = page.evaluate(f"window.location.origin + '?session_id={session_id}'")
        context = page.context
        page.close()
        new_page = context.new_page()
        new_page.goto(resume_url)
        new_page.wait_for_load_state("networkidle")

        # Step 3: Verify context preservation
        print("Step 3: Verifying context preservation")
        resumed_session_id = new_page.evaluate("localStorage.getItem('unobot_session_id')")
        assert resumed_session_id == session_id, "Session ID should be preserved"

        # Check if client name appears in conversation
        chat_button = new_page.get_by_test_id("chat-widget-button")
        chat_button.click()
        new_page.wait_for_selector('[data-testid="messages-container"]')

        messages = new_page.locator('[data-testid="messages-container"] .bg-white').all()
        client_name_found = False

        for msg_element in messages:
            msg_text = msg_element.inner_text()
            if "John Smith" in msg_text or "john" in msg_text.lower():
                client_name_found = True
                print(f"✓ Client name found in resumed session: 'John Smith'")
                break

        assert client_name_found, "Client information should be preserved in resumed session"

        # Verify business context is preserved
        business_context_found = False
        for msg_element in messages:
            msg_text = msg_element.inner_text()
            if "healthcare" in msg_text.lower() or "patient analytics" in msg_text.lower():
                business_context_found = True
                print(f"✓ Business context found in resumed session")
                break

        assert business_context_found, "Business context should be preserved in resumed session"

        new_page.close()

    def test_session_resume_with_empty_conversation(self, page: Page):
        """
        Test: Resuming a session that has minimal conversation history

        Steps:
        1. Create session with just welcome message
        2. Resume session
        3. Verify minimal history is preserved
        """
        print("\n=== Test: Resume Session with Minimal History ===")

        # Step 1: Create session with just welcome message
        print("Step 1: Creating session with minimal history")
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        page.wait_for_selector('[data-testid="messages-container"]')

        session_id = page.evaluate("localStorage.getItem('unobot_session_id')")
        print(f"✓ Session ID: {session_id}")

        # Wait for welcome message to load
        page.wait_for_timeout(2000)

        # Get initial message count
        initial_messages = page.locator('[data-testid="messages-container"] .bg-white').all()
        initial_count = len(initial_messages)
        print(f"✓ Initial message count: {initial_count}")

        # Step 2: Resume session
        print("Step 2: Resuming session")
        resume_url = page.evaluate(f"window.location.origin + '?session_id={session_id}'")
        context = page.context
        page.close()
        new_page = context.new_page()
        new_page.goto(resume_url)
        new_page.wait_for_load_state("networkidle")

        # Step 3: Verify minimal history is preserved
        print("Step 3: Verifying minimal history preservation")
        resumed_session_id = new_page.evaluate("localStorage.getItem('unobot_session_id')")
        assert resumed_session_id == session_id, "Session ID should be preserved"

        chat_button = new_page.get_by_test_id("chat-widget-button")
        chat_button.click()
        new_page.wait_for_selector('[data-testid="messages-container"]')

        resumed_messages = new_page.locator('[data-testid="messages-container"] .bg-white').all()
        resumed_count = len(resumed_messages)
        print(f"✓ Resumed message count: {resumed_count}")

        assert resumed_count == initial_count, \
            f"Message count should be preserved. Initial: {initial_count}, Resumed: {resumed_count}"

        # Verify welcome message is present
        welcome_found = False
        for msg_element in resumed_messages:
            msg_text = msg_element.inner_text()
            if "Welcome" in msg_text or "UnoBot" in msg_text:
                welcome_found = True
                print(f"✓ Welcome message found in resumed session")
                break

        assert welcome_found, "Welcome message should be preserved in resumed session"

        new_page.close()

    def test_session_resume_url_generation(self, page: Page):
        """
        Test: Session resume URLs are generated correctly

        Steps:
        1. Create session and generate URL
        2. Verify URL format
        3. Test URL functionality
        """
        print("\n=== Test: Session Resume URL Generation ===")

        # Step 1: Create session and generate URL
        print("Step 1: Creating session and generating resume URL")
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        page.wait_for_selector('[data-testid="messages-container"]')

        session_id = page.evaluate("localStorage.getItem('unobot_session_id')")
        print(f"✓ Session ID: {session_id}")

        # Generate resume URL
        resume_url = page.evaluate(f"window.location.origin + '?session_id={session_id}'")
        print(f"✓ Generated resume URL: {resume_url}")

        # Step 2: Verify URL format
        print("Step 2: Verifying URL format")
        assert resume_url is not None, "Resume URL should be generated"
        assert 'session_id=' in resume_url, "URL should contain session_id parameter"
        assert session_id in resume_url, "URL should contain the actual session ID"

        # Check that URL uses current origin
        current_origin = page.evaluate("window.location.origin")
        assert current_origin in resume_url, "URL should use current origin"

        # Step 3: Test URL functionality
        print("Step 3: Testing URL functionality")
        context = page.context
        page.close()
        new_page = context.new_page()
        new_page.goto(resume_url)
        new_page.wait_for_load_state("networkidle")

        # Verify session is resumed
        resumed_session_id = new_page.evaluate("localStorage.getItem('unobot_session_id')")
        assert resumed_session_id == session_id, "Session should be resumed via generated URL"

        new_page.close()

    def test_session_resume_multiple_times(self, page: Page):
        """
        Test: A session can be resumed multiple times via email links

        Steps:
        1. Create initial session
        2. First resume
        3. Second resume
        4. Third resume
        5. Verify conversation history is consistent across resumes
        """
        print("\n=== Test: Multiple Session Resumes ===")

        # Step 1: Create initial session
        print("Step 1: Creating initial session")
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        page.wait_for_selector('[data-testid="messages-container"]')

        session_id = page.evaluate("localStorage.getItem('unobot_session_id')")
        print(f"✓ Session ID: {session_id}")

        # Add some conversation
        message_input = page.get_by_placeholder("Type your message...")
        message_input.fill("This is test message for multiple resume")
        message_input.press("Enter")
        page.wait_for_timeout(3000)

        initial_messages = page.locator('[data-testid="messages-container"] .bg-white').all()
        initial_count = len(initial_messages)
        print(f"✓ Initial message count: {initial_count}")

        # Get resume URL
        resume_url = page.evaluate(f"window.location.origin + '?session_id={session_id}'")
        print(f"✓ Resume URL: {resume_url}")

        context = page.context

        # Step 2: First resume
        print("Step 2: First resume")
        page.close()
        page1 = context.new_page()
        page1.goto(resume_url)
        page1.wait_for_load_state("networkidle")

        resumed_session_id = page1.evaluate("localStorage.getItem('unobot_session_id')")
        assert resumed_session_id == session_id, "First resume should work"

        # Step 3: Second resume
        print("Step 3: Second resume")
        page1.close()
        page2 = context.new_page()
        page2.goto(resume_url)
        page2.wait_for_load_state("networkidle")

        resumed_session_id_2 = page2.evaluate("localStorage.getItem('unobot_session_id')")
        assert resumed_session_id_2 == session_id, "Second resume should work"

        # Step 4: Third resume
        print("Step 4: Third resume")
        page2.close()
        page3 = context.new_page()
        page3.goto(resume_url)
        page3.wait_for_load_state("networkidle")

        resumed_session_id_3 = page3.evaluate("localStorage.getItem('unobot_session_id')")
        assert resumed_session_id_3 == session_id, "Third resume should work"

        # Step 5: Verify conversation history is consistent across resumes
        print("Step 5: Verifying conversation history consistency")
        for i, test_page in enumerate([page1, page2, page3], 1):
            if test_page.is_closed():
                test_page = context.new_page()
                test_page.goto(resume_url)
                test_page.wait_for_load_state("networkidle")

            chat_button = test_page.get_by_test_id("chat-widget-button")
            chat_button.click()
            test_page.wait_for_selector('[data-testid="messages-container"]')

            messages = test_page.locator('[data-testid="messages-container"] .bg-white').all()
            message_count = len(messages)
            print(f"✓ Resume {i}: {message_count} messages")

            assert message_count == initial_count, \
                f"Resume {i} should have same message count as initial. Initial: {initial_count}, Resume {i}: {message_count}"

            # Check for the test message
            test_message_found = False
            for msg_element in messages:
                msg_text = msg_element.inner_text()
                if "test message for multiple resume" in msg_text:
                    test_message_found = True
                    break

            assert test_message_found, f"Test message should be present in resume {i}"

            if not test_page.is_closed():
                test_page.close()

        print("✓ All multiple resume tests passed")

    def test_session_resume_chat_widget_behavior(self, page: Page):
        """
        Test: Chat widget behavior is correct after session resume

        Steps:
        1. Create session and close chat
        2. Resume session
        3. Test chat widget behavior
        """
        print("\n=== Test: Chat Widget Behavior After Resume ===")

        # Step 1: Create session and close chat
        print("Step 1: Creating session and closing chat")
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()
        page.wait_for_selector('[data-testid="messages-container"]')

        session_id = page.evaluate("localStorage.getItem('unobot_session_id')")
        print(f"✓ Session ID: {session_id}")

        # Send a message
        message_input = page.get_by_placeholder("Type your message...")
        message_input.fill("Testing chat widget behavior")
        message_input.press("Enter")
        page.wait_for_timeout(3000)

        # Close chat window
        close_button = page.get_by_test_id("close-button")
        close_button.click()
        page.wait_for_timeout(1000)

        # Step 2: Resume session
        print("Step 2: Resuming session")
        resume_url = page.evaluate(f"window.location.origin + '?session_id={session_id}'")
        context = page.context
        page.close()
        new_page = context.new_page()
        new_page.goto(resume_url)
        new_page.wait_for_load_state("networkidle")

        # Step 3: Test chat widget behavior
        print("Step 3: Testing chat widget behavior")

        # Verify session ID is preserved
        resumed_session_id = new_page.evaluate("localStorage.getItem('unobot_session_id')")
        assert resumed_session_id == session_id, "Session should be resumed"

        # Test 1: Chat widget should be closed initially
        chat_window = new_page.locator('[data-testid="chat-window"]')
        is_open = chat_window.is_visible()
        assert not is_open, "Chat window should be closed initially after resume"

        # Test 2: Clicking chat button should open existing session
        chat_button = new_page.get_by_test_id("chat-widget-button")
        chat_button.click()
        new_page.wait_for_selector('[data-testid="chat-window"]')
        expect(new_page.locator('[data-testid="chat-window"]')).to_be_visible()

        # Test 3: Conversation should be visible
        messages_container = new_page.locator('[data-testid="messages-container"]')
        expect(messages_container).to_be_visible()

        messages = new_page.locator('[data-testid="messages-container"] .bg-white').all()
        assert len(messages) > 0, "Messages should be visible after opening chat"

        # Test 4: Should be able to send new messages
        message_input = new_page.get_by_placeholder("Type your message...")
        test_message = "Testing new message after resume"
        message_input.fill(test_message)
        message_input.press("Enter")
        new_page.wait_for_timeout(3000)

        # Verify new message was sent
        new_messages = new_page.locator('[data-testid="messages-container"] .bg-white').all()
        new_message_found = False
        for msg_element in new_messages:
            msg_text = msg_element.inner_text()
            if test_message in msg_text:
                new_message_found = True
                break

        assert new_message_found, "New message should be sent after resume"

        new_page.close()

    def test_session_resume_url_parameter_handling(self, page: Page):
        """
        Test: Session ID in URL parameter is properly handled

        Steps:
        1. Navigate to URL with session_id parameter
        2. Verify session ID is stored in localStorage
        """
        print("\n=== Test: URL Parameter Handling ===")

        # Create a test session ID
        test_session_id = "test-session-123"

        # Navigate to URL with session_id parameter
        test_url = f"http://localhost:5173?session_id={test_session_id}"
        page.goto(test_url)
        page.wait_for_load_state("networkidle")

        # Verify session ID is stored in localStorage
        stored_session_id = page.evaluate("localStorage.getItem('unobot_session_id')")
        assert stored_session_id == test_session_id, \
            f"Expected {test_session_id}, got {stored_session_id}"

        print(f"✓ Successfully stored session ID: {stored_session_id}")

    def test_session_resume_without_parameter(self, page: Page):
        """
        Test: Normal session creation works when no session_id parameter is provided

        Steps:
        1. Navigate to root URL without session_id parameter
        2. Open chat to create new session
        3. Verify new session is created
        """
        print("\n=== Test: Session Creation Without Parameter ===")

        # Navigate to root URL without session_id parameter
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Session ID should be null initially
        initial_session_id = page.evaluate("localStorage.getItem('unobot_session_id')")
        assert initial_session_id is None, "No session should exist initially"

        # Open chat to create new session
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for session to be created
        page.wait_for_timeout(1000)

        # Now session should be created
        created_session_id = page.evaluate("localStorage.getItem('unobot_session_id')")
        assert created_session_id is not None, "Session should be created when chat is opened"

        print(f"✓ New session created: {created_session_id}")
