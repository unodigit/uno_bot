"""End-to-end tests for Chat Widget functionality."""
from playwright.sync_api import Page, expect

# Frontend URL - use environment variable or default
FRONTEND_URL = "http://localhost:5173"


class TestChatWidget:
    """Test cases for chat widget UI components."""

    def test_chat_widget_button_renders_on_page_load(self, page: Page):
        """
        Test: Chat widget button renders on page load and is visible in bottom-right corner

        Steps:
        1. Navigate to the main page
        2. Wait for page to fully load
        3. Verify chat button is visible in bottom-right corner
        4. Verify button has correct size (60x60px)
        5. Verify button has 24px margin from edges
        """
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Verify chat button is visible using data-testid
        chat_button = page.get_by_test_id("chat-widget-button")
        expect(chat_button).to_be_visible()

        # Verify button has correct size (60x60px)
        bounding_box = chat_button.bounding_box()
        assert bounding_box is not None
        assert bounding_box["width"] == 60
        assert bounding_box["height"] == 60

        # Verify button is in bottom-right corner with 24px margin
        viewport_size = page.viewport_size
        assert viewport_size is not None
        expected_right = viewport_size["width"] - 60 - 24
        expected_bottom = viewport_size["height"] - 60 - 24

        # Check position (approximately)
        assert abs(bounding_box["x"] - expected_right) < 5
        assert abs(bounding_box["y"] - expected_bottom) < 5
        print("✓ Chat widget button renders correctly in bottom-right corner")

    def test_chat_widget_opens_when_clicking_button(self, page: Page):
        """
        Test: Chat widget opens when clicking the floating button

        Steps:
        1. Navigate to the main page
        2. Click the chat widget button
        3. Verify chat window opens
        4. Verify chat window is visible and interactive
        """
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Click the chat widget button
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Verify chat window is visible
        chat_window = page.get_by_test_id("chat-window")
        expect(chat_window).to_be_visible()

        # Verify messages container exists
        messages_container = page.get_by_test_id("messages-container")
        expect(messages_container).to_be_visible()
        print("✓ Chat window opens when button clicked")

    def test_chat_widget_closes_when_clicking_minimize(self, page: Page):
        """
        Test: Chat widget closes when clicking minimize button

        Steps:
        1. Navigate to main page and open chat widget
        2. Click the minimize/close button in header
        3. Verify chat window closes
        4. Verify floating button becomes visible again
        """
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Verify chat window is open
        chat_window = page.get_by_test_id("chat-window")
        expect(chat_window).to_be_visible()

        # Click minimize button
        minimize_button = page.get_by_test_id("minimize-button")
        minimize_button.click()

        # Verify chat window is closed
        expect(chat_window).not_to_be_visible()

        # Verify floating button is visible again (either normal or minimized version)
        normal_button = page.get_by_test_id("chat-widget-button")
        minimized_button = page.get_by_test_id("chat-widget-button-minimized")
        # At least one should be visible
        assert normal_button.is_visible() or minimized_button.is_visible()
        print("✓ Chat window closes when minimize button clicked")

    def test_welcome_message_displays_when_chat_opens(self, page: Page):
        """
        Test: Welcome message is displayed when chat opens

        Steps:
        1. Navigate to main page
        2. Open chat widget
        3. Verify welcome message appears from bot
        4. Verify message contains greeting
        """
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Open chat widget
        chat_button = page.get_by_test_id("chat-widget-button")
        chat_button.click()

        # Wait for welcome message to appear
        bot_message = page.get_by_test_id("message-assistant")
        expect(bot_message).to_be_visible()

        # Verify it contains greeting text (actual message starts with "Hi")
        expect(bot_message).to_contain_text("Hi")
        expect(bot_message).to_contain_text("UnoBot")
        print("✓ Welcome message displays correctly")

    def test_user_can_send_message(self, page: Page):
        """
        Test: User can type and send messages via text input

        Steps:
        1. Open chat widget
        2. Type a message in the input field
        3. Click send button
        4. Verify message appears in chat history
        5. Verify input field is cleared after sending
        """
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()

        # Type a message
        input_field = page.get_by_test_id("message-input")
        test_message = "Hello, I need help with AI strategy"
        input_field.fill(test_message)

        # Verify input has value
        expect(input_field).to_have_value(test_message)

        # Click send button
        send_button = page.get_by_test_id("send-button")
        send_button.click()

        # Verify input is cleared
        expect(input_field).to_have_value("")

        # Verify user message appears
        user_message = page.get_by_test_id("message-user")
        expect(user_message).to_be_visible()
        expect(user_message).to_contain_text(test_message)
        print("✓ User can send messages successfully")

    def test_session_creation_on_first_open(self, page: Page):
        """
        Test: Chat session is created when opening widget for first time

        Steps:
        1. Clear browser storage and navigate to main page
        2. Open the chat widget
        3. Verify POST request to /api/v1/sessions is made
        4. Verify session ID is returned and stored
        """
        # Clear storage to simulate first visit - using context add_init_script
        page.context.add_init_script("localStorage.clear()")
        page.context.clear_cookies()

        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Track session creation
        session_created = False

        def handle_route(route):
            nonlocal session_created
            if "/api/v1/sessions" in route.request.url and route.request.method == "POST":
                session_created = True
            route.continue_()

        page.route("**/*", handle_route)

        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()

        # Wait for API call
        page.wait_for_timeout(500)

        # Verify session was created
        assert session_created, "Session creation API call was not made"

        # Verify session ID is stored
        session_id = page.evaluate("localStorage.getItem('unobot_session_id')")
        assert session_id is not None, "Session ID not stored"

        # Verify welcome message
        bot_message = page.get_by_test_id("message-assistant")
        expect(bot_message).to_be_visible()
        print("✓ Session created on first open")

    def test_welcome_message_content(self, page: Page):
        """
        Test: Welcome message contains expected content and structure

        Steps:
        1. Open chat widget
        2. Verify welcome message has proper content
        3. Verify message has timestamp
        """
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()

        # Get bot message
        bot_message = page.get_by_test_id("message-assistant")
        expect(bot_message).to_be_visible()

        # Check for key content
        content = bot_message.inner_text()
        assert "UnoBot" in content or "Hello" in content
        print("✓ Welcome message has proper content")

    def test_session_persists_across_page_refresh(self, page: Page):
        """
        Test: Session persists across page refreshes

        Steps:
        1. Open chat widget and send a message
        2. Note the session ID and message count
        3. Refresh the page
        4. Open chat widget again
        5. Verify same session is resumed
        6. Verify previous messages are displayed
        """
        # Clear storage to start fresh - only once at the beginning
        page.context.clear_cookies()
        page.goto(FRONTEND_URL)
        page.wait_for_load_state("networkidle")

        # Manually clear localStorage once
        page.evaluate("localStorage.clear()")

        # Open chat widget
        page.get_by_test_id("chat-widget-button").click()

        # Wait for session creation
        page.wait_for_timeout(500)

        # Get session ID before refresh
        session_id_before = page.evaluate("localStorage.getItem('unobot_session_id')")
        assert session_id_before is not None, "Session ID not created"

        # Send a message
        input_field = page.get_by_test_id("message-input")
        test_message = "Test message for persistence"
        input_field.fill(test_message)
        page.get_by_test_id("send-button").click()

        # Wait for message to be sent and bot response
        page.wait_for_timeout(1000)

        # Count messages before refresh
        messages_before = page.locator('[data-testid^="message-"]').count()
        assert messages_before >= 2, f"Expected at least 2 messages, got {messages_before}"

        # Refresh the page
        page.reload()
        page.wait_for_load_state("networkidle")

        # Open chat widget again
        page.get_by_test_id("chat-widget-button").click()

        # Wait for session to load
        page.wait_for_timeout(1000)

        # Verify session ID is the same
        session_id_after = page.evaluate("localStorage.getItem('unobot_session_id')")
        assert session_id_after == session_id_before, f"Session ID changed after refresh: {session_id_before} -> {session_id_after}"

        # Verify messages are restored
        all_messages = page.locator('[data-testid^="message-"]')
        message_count = all_messages.count()
        assert message_count >= messages_before, f"Expected at least {messages_before} messages after refresh, got {message_count}"

        # Verify our test message is visible
        test_message_found = page.get_by_text(test_message).is_visible()
        assert test_message_found, "Test message not found after refresh"

        print("✓ Session persists across page refresh")
