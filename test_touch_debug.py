from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 375, "height": 812})
    page = context.new_page()

    # Navigate with domcontentloaded
    page.goto("http://localhost:5173", wait_until="domcontentloaded")
    time.sleep(5)

    # Check what's on the page
    body = page.locator("body")
    html = body.inner_html()

    # Check if chat-widget-button exists
    if "chat-widget-button" in html:
        print("✓ chat-widget-button found in HTML")

        # Now try to get it via Playwright
        try:
            chat_button = page.get_by_test_id("chat-widget-button")
            if chat_button.is_visible():
                box = chat_button.bounding_box()
                print(f"✓ Button visible: {box['width']:.1f}x{box['height']:.1f}px")
            else:
                print("✗ Button exists but not visible")
        except Exception as e:
            print(f"✗ Error getting button: {e}")
    else:
        print("✗ chat-widget-button NOT found in HTML")
        print(f"HTML snippet: {html[:500]}")

    browser.close()
