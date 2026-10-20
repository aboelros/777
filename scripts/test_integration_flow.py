import json
import time
from playwright.sync_api import sync_playwright
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cursor_helper import inject_cursor, smooth_move, move_and_click

MOCK_PROJECT = {
    "id": "c1f7a0b2-4d8e-4b6a-9a8f-2e3d4c5b6a7b",
    "name": "AI Sales Commander Demo Store",
    "domain": "store.example.com",
    "currency": "USD"
}

def test_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True
        )
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        def route_handler(route):
            url = route.request.url
            if "/api/v1/projects" in url:
                route.fulfill(status=200, content_type="application/json", body=json.dumps([MOCK_PROJECT]))
            elif "/meta/auth-url" in url:
                route.fulfill(status=200, content_type="application/json", body=json.dumps({
                    "auth_url": "http://127.0.0.1:5173/integrations/meta/callback?code=mock_meta_review_code_999&state=auth_ok"
                }))
            elif "/meta/callback" in url:
                route.fulfill(status=200, content_type="application/json", body=json.dumps({
                    "access_token": "EAAGm0PX4ZCpsBA...",
                    "accounts": [
                        {
                            "id": "10029384819",
                            "name": "AI Sales Commander Official Page",
                            "category": "E-Commerce",
                            "access_token": "EAAGm0PX4ZCps...",
                            "instagram_business_account": {
                                "id": "1784140029384819",
                                "username": "aisalescommander_official",
                                "name": "AI Sales Commander Official"
                            }
                        }
                    ],
                    "whatsapp_accounts": [
                        {
                            "id": "109283746",
                            "display_phone_number": "+1 (555) 019-2834",
                            "verified_name": "AI Sales Commander",
                            "waba_id": "987654321098"
                        }
                    ]
                }))
            elif "/connect" in url:
                route.fulfill(status=200, content_type="application/json", body=json.dumps({"success": True}))
            elif "/api/v1/integrations" in url:
                route.fulfill(status=200, content_type="application/json", body=json.dumps([]))
            else:
                route.continue_()

        page.route("**/api/v1/**", route_handler)

        page.goto("http://127.0.0.1:5173/")
        page.evaluate(f"""() => {{
            localStorage.setItem('project-storage', JSON.stringify({{
                state: {{
                    currentProject: {json.dumps(MOCK_PROJECT)},
                    projects: [{json.dumps(MOCK_PROJECT)}]
                }}
            }}));
            localStorage.setItem('auth-storage', JSON.stringify({{
                state: {{
                    user: {{ name: 'Meta Reviewer', email: 'reviewer@example.com' }},
                    isAuthenticated: true
                }}
            }}));
        }}""")

        # 1. Integrations page
        page.goto("http://127.0.0.1:5173/integrations")
        inject_cursor(page)
        page.wait_for_timeout(2000)

        # 2. Click Facebook Messenger card to open connect modal
        fb_card = page.locator("h3:has-text('Facebook Messenger')").first
        if fb_card.is_visible():
            move_and_click(page, fb_card)
            page.wait_for_timeout(2000)

        # 3. Click Continue with Meta Business
        meta_btn = page.locator("button:has-text('Continue with Meta Business')").first
        if meta_btn.is_visible():
            move_and_click(page, meta_btn)
            page.wait_for_timeout(3000)

        # 4. Now on MetaCallback page
        page.screenshot(path="test_callback_page.png")
        print("Current URL:", page.url)

        # Select account card
        account_card = page.locator("text=AI Sales Commander Official Page").first
        if account_card.is_visible():
            move_and_click(page, account_card)
            page.wait_for_timeout(1000)

        # Click Connect Selected Channel
        connect_btn = page.locator("button:has-text('Connect Selected Channel')").first
        if connect_btn.is_visible():
            move_and_click(page, connect_btn)
            page.wait_for_timeout(2000)

        page.screenshot(path="test_post_connect.png")
        print("Post connect URL:", page.url)

        browser.close()

if __name__ == "__main__":
    test_flow()
