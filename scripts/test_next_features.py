#!/usr/bin/env python3
"""
Test script to verify the next set of features:
- Feature 4: Chat session creation
- Feature 5: Welcome message display
- Feature 6: User message sending
- Feature 7: Bot response
"""

from playwright.sync_api import sync_playwright
import sys
import time
import json

FRONTEND_URL = "http://localhost:5173"
API_URL = "http://localhost:8000"

def test_feature_4_session_creation():
    """Test: Chat session is created when opening widget for first time"""
    print("\n" + "="*60)
    print("Feature 4: Chat session creation")
    print("="*60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a fresh context for this test
        context = browser.new_context()
        page = context.new_page()

        try:
            # Track session creation via API interception
            session_created = []

            def handle_route(route):
                req = route.request
                if '/api/v1/sessions' in req.url and req.method == 'POST':
                    response = route.fetch()
                    body = json.loads(response.body())
                    session_created.append(body.get('id'))
                route.continue_()

            page.route('**/*', handle_route)

            # Navigate and open chat
            print("1. Navigating to page...")
            page.goto(FRONTEND_URL, timeout=10000)
            page.wait_for_load_state("networkidle")

            print("2. Opening chat widget...")
            chat_button = page.get_by_test_id("chat-widget-button")
            chat_button.click()
            page.wait_for_timeout(1000)

            # Verify session was created
            print("3. Checking session creation...")
            assert len(session_created) > 0, "No session creation API call was made"

            # Should only create ONE session
            assert len(session_created) == 1, f"Expected 1 session, got {len(session_created)}: {session_created}"

            print(f"   ✓ Session created: {session_created[0]}")

            # Verify session ID is stored (check via API response, not localStorage)
            # We can verify by checking that the welcome message appears
            bot_message = page.get_by_test_id("message-assistant")
            assert bot_message.is_visible(), "Welcome message not visible"
            print("   ✓ Welcome message displayed (session is active)")

            return True

        except Exception as e:
            print(f"   ✗ Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()


def test_feature_5_welcome_message():
    """Test: Welcome message is displayed when chat opens"""
    print("\n" + "="*60)
    print("Feature 5: Welcome message display")
    print("="*60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        try:
            print("1. Navigating to page...")
            page.goto(FRONTEND_URL, timeout=10000)
            page.wait_for_load_state("networkidle")

            print("2. Opening chat widget...")
            page.get_by_test_id("chat-widget-button").click()
            page.wait_for_timeout(500)

            print("3. Checking for welcome message...")
            bot_message = page.get_by_test_id("message-assistant")
            assert bot_message.is_visible(), "Bot message not visible"

            content = bot_message.inner_text()
            print(f"   Message content: {content[:100]}...")

            # Check for key elements
            assert "UnoBot" in content or "Hello" in content or "Hi" in content, "Welcome message missing greeting"
            print("   ✓ Welcome message displayed correctly")

            return True

        except Exception as e:
            print(f"   ✗ Failed: {e}")
            return False
        finally:
            browser.close()


def test_feature_6_user_message_sending():
    """Test: User can type and send messages via text input"""
    print("\n" + "="*60)
    print("Feature 6: User message sending")
    print("="*60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        try:
            print("1. Navigating and opening chat...")
            page.goto(FRONTEND_URL, timeout=10000)
            page.wait_for_load_state("networkidle")
            page.get_by_test_id("chat-widget-button").click()
            page.wait_for_timeout(500)

            print("2. Typing message...")
            test_message = "Hello, I need help with AI strategy"
            input_field = page.get_by_test_id("message-input")
            input_field.fill(test_message)

            # Verify input has value
            value = input_field.input_value()
            assert value == test_message, f"Input value mismatch: {value}"
            print(f"   ✓ Input field contains: '{test_message}'")

            print("3. Sending message...")
            send_button = page.get_by_test_id("send-button")
            send_button.click()

            # Wait for message to appear and input to clear
            page.wait_for_timeout(1000)

            # Verify input is cleared
            value_after = input_field.input_value()
            assert value_after == "", f"Input not cleared: {value_after}"
            print("   ✓ Input cleared after sending")

            # Verify user message appears (check that there's a user message element)
            user_message = page.locator('[data-testid="message-user"]').last
            assert user_message.is_visible(), "User message not visible"

            # The message might have timestamp appended, so just check it contains the text
            msg_text = user_message.inner_text()
            assert test_message in msg_text, f"Expected '{test_message}' in '{msg_text}'"
            print("   ✓ User message appears in chat")

            return True

        except Exception as e:
            print(f"   ✗ Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()


def test_feature_7_bot_response():
    """Test: Bot responds to user messages"""
    print("\n" + "="*60)
    print("Feature 7: Bot response")
    print("="*60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        try:
            print("1. Setting up chat...")
            page.goto(FRONTEND_URL, timeout=10000)
            page.wait_for_load_state("networkidle")
            page.get_by_test_id("chat-widget-button").click()
            page.wait_for_timeout(500)

            print("2. Sending message...")
            input_field = page.get_by_test_id("message-input")
            input_field.fill("What AI services do you offer?")
            page.get_by_test_id("send-button").click()

            print("3. Waiting for bot response...")
            # Wait for typing indicator to appear
            try:
                page.wait_for_selector('[data-testid="typing-indicator"]', timeout=5000)
                print("   ✓ Typing indicator appeared")
            except:
                print("   ⚠ Typing indicator skipped (response was fast)")

            # Wait for typing indicator to disappear
            page.wait_for_selector('[data-testid="typing-indicator"]', state='hidden', timeout=30000)
            print("   ✓ Typing indicator disappeared")

            # Check for new bot message (should have at least 2 now - welcome + response)
            page.wait_for_timeout(500)
            bot_messages = page.locator('[data-testid="message-assistant"]').count()
            print(f"   Bot messages after response: {bot_messages}")

            # Should have at least 2 bot messages (welcome + response)
            assert bot_messages >= 2, f"Expected at least 2 bot messages, got {bot_messages}"
            print("   ✓ Bot responded to user message")

            return True

        except Exception as e:
            print(f"   ✗ Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("UnoBot Feature Verification Tests")
    print("="*60)

    results = []

    # Run tests
    results.append(("Feature 4: Session Creation", test_feature_4_session_creation()))
    results.append(("Feature 5: Welcome Message", test_feature_5_welcome_message()))
    results.append(("Feature 6: User Message Sending", test_feature_6_user_message_sending()))
    results.append(("Feature 7: Bot Response", test_feature_7_bot_response()))

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
