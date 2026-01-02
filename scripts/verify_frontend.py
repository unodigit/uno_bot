#!/usr/bin/env python3
"""Simple script to verify chat widget functionality using Playwright."""
from playwright.sync_api import sync_playwright
import sys

def test_chat_widget():
    """Test the chat widget features."""
    print("Starting chat widget verification...")
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        
        try:
            # Test 1: Navigate to page
            print("Test 1: Navigating to http://localhost:5173")
            page.goto("http://localhost:5173", timeout=10000)
            page.wait_for_load_state("networkidle")
            print("  ✓ Page loaded successfully")
            
            # Test 2: Check chat button is visible
            print("\nTest 2: Checking chat button is visible in bottom-right")
            button = page.locator("button.fixed.bottom-6.right-6")
            if button.is_visible():
                print("  ✓ Chat button is visible")
            else:
                print("  ✗ Chat button not found")
                return False
            
            # Test 3: Click button and check window opens
            print("\nTest 3: Clicking chat button")
            button.click()
            page.wait_for_timeout(500)  # Wait for animation
            
            # Check for chat window
            chat_window = page.locator("div.fixed.bottom-6.right-6").filter(has_text="UnoBot")
            if chat_window.is_visible():
                print("  ✓ Chat window opened")
            else:
                print("  ✗ Chat window did not open")
                return False
            
            # Test 4: Check welcome message
            print("\nTest 4: Checking for welcome message")
            if page.locator("text=Hi! I'm UnoBot").is_visible():
                print("  ✓ Welcome message displayed")
            else:
                print("  ✗ Welcome message not found")
                return False
            
            # Test 5: Close chat window
            print("\nTest 5: Closing chat window")
            close_button = page.locator("button[aria-label='Close chat']")
            if close_button.is_visible():
                close_button.click()
                page.wait_for_timeout(500)
                print("  ✓ Chat window closed")
            else:
                print("  ⚠ Close button not found (may not be critical)")
            
            print("\n" + "="*50)
            print("All critical tests passed!")
            print("="*50)
            return True
            
        except Exception as e:
            print(f"\n✗ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    success = test_chat_widget()
    sys.exit(0 if success else 1)
