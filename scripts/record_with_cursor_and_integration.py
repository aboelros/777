import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cursor_helper import inject_cursor, smooth_move, move_and_click

MOCK_PROJECT = {
    "id": "c1f7a0b2-4d8e-4b6a-9a8f-2e3d4c5b6a7b",
    "name": "AI Sales Commander Demo Store",
    "domain": "store.example.com",
    "currency": "USD"
}

MOCK_CHANNELS_BEFORE = [
    {
        "id": "shopify-1",
        "provider": "shopify",
        "status": "connected",
        "config": {"shop_name": "aisales-store.myshopify.com"},
        "created_at": "2026-01-10T12:00:00Z"
    }
]

MOCK_CHANNELS_AFTER = [
    {
        "id": "meta-fb-1",
        "provider": "facebook",
        "status": "connected",
        "config": {"page_name": "AI Sales Commander Official Page", "page_id": "10029384819"},
        "created_at": "2026-01-10T12:00:00Z"
    },
    {
        "id": "meta-ig-1",
        "provider": "instagram",
        "status": "connected",
        "config": {"instagram_username": "aisalescommander_official", "page_id": "10029384819", "instagram_business_account_id": "1784140029384819"},
        "created_at": "2026-01-10T12:00:00Z"
    },
    {
        "id": "meta-wa-1",
        "provider": "whatsapp",
        "status": "connected",
        "config": {"phone_number": "+1 (555) 019-2834", "phone_number_id": "109283746", "waba_id": "987654321098"},
        "created_at": "2026-01-10T12:00:00Z"
    },
    {
        "id": "shopify-1",
        "provider": "shopify",
        "status": "connected",
        "config": {"shop_name": "aisales-store.myshopify.com"},
        "created_at": "2026-01-10T12:00:00Z"
    }
]

MOCK_CONVERSATIONS = [
    {"id": "conv-1", "customer_name": "Sarah Connor", "customer_email": "sarah.c@example.com", "channel": "instagram", "last_message": "Is this evening dress available in size Medium?", "unread_count": 1},
    {"id": "conv-2", "customer_name": "David Miller", "customer_email": "david.m@example.com", "channel": "facebook", "last_message": "Hello, do you offer express courier delivery to London?", "unread_count": 0},
    {"id": "conv-3", "customer_name": "Elena Rostova", "customer_email": "elena.r@example.com", "channel": "whatsapp", "last_message": "Could you send me the tracking link for order #8492?", "unread_count": 2}
]

MOCK_MESSAGES = {
    "conv-1": [
        {"id": "m1", "sender": "customer", "content": "Hello! I saw your new collection on Instagram. Is the silk evening dress available in Medium?", "created_at": "2026-10-20T10:14:00Z"},
        {"id": "m2", "sender": "user", "content": "Hi Sarah! Yes, we have 4 units left in Medium. Would you like me to reserve one for you?", "created_at": "2026-10-20T10:15:30Z"},
        {"id": "m3", "sender": "customer", "content": "Yes please! And what are the delivery times?", "created_at": "2026-10-20T10:16:10Z"}
    ],
    "conv-2": [
        {"id": "m4", "sender": "customer", "content": "Hello, do you offer express delivery to London?", "created_at": "2026-10-20T09:40:00Z"},
        {"id": "m5", "sender": "user", "content": "Yes David! We ship with DHL Express, arriving within 2 business days.", "created_at": "2026-10-20T09:42:00Z"}
    ],
    "conv-3": [
        {"id": "m6", "sender": "customer", "content": "Could you send me the tracking link for order #8492?", "created_at": "2026-10-20T08:30:00Z"}
    ]
}

MOCK_COMMENTS = [
    {"id": "comm-1", "author_name": "Jessica Vance", "platform": "instagram", "text": "Are these shoes true to size? Love the design!", "responded": False, "created_at": "2026-10-20T09:30:00Z"},
    {"id": "comm-2", "author_name": "Marcus Aurelius", "platform": "facebook", "text": "Do you provide international warranty on the smart watches?", "responded": True, "created_at": "2026-10-20T08:15:00Z"},
    {"id": "comm-3", "author_name": "Chloe Dupont", "platform": "instagram", "text": "When will the beige coat be back in stock?", "responded": False, "created_at": "2026-10-20T11:00:00Z"}
]

connected_state = {"connected": False}

def setup_interception(page):
    def route_handler(route):
        url = route.request.url
        if "/api/v1/projects" in url and route.request.method == "GET":
            route.fulfill(status=200, content_type="application/json", body=json.dumps([MOCK_PROJECT]))
        elif "/meta/auth-url" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "auth_url": "http://127.0.0.1:5173/integrations/meta/callback?code=mock_meta_review_token_777&state=auth_ok"
            }))
        elif "/meta/callback" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({
                "access_token": "EAAGm0PX4ZCpsBAK...",
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
            connected_state["connected"] = True
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"success": True}))
        elif "/api/v1/integrations" in url:
            data = MOCK_CHANNELS_AFTER if connected_state["connected"] else MOCK_CHANNELS_BEFORE
            route.fulfill(status=200, content_type="application/json", body=json.dumps(data))
        elif "/api/v1/messages" in url and "conversations" in url and "messages" not in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_CONVERSATIONS))
        elif "/messages/" in url and "/messages" in url:
            cid = "conv-1"
            for k in MOCK_MESSAGES:
                if k in url:
                    cid = k
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_MESSAGES.get(cid, [])))
        elif "/social/" in url and "comments" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_COMMENTS))
        elif "/social/" in url and "stats" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps({"total_comments": 142, "unanswered_comments": 3, "avg_response_time": "4m"}))
        elif "/social/" in url and "feed" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps([
                {"id": "p1", "caption": "Autumn 2026 Collection is now live. ✨", "comments_count": 48, "like_count": 1420}
            ]))
        else:
            route.continue_()

    page.route("**/api/v1/**", route_handler)

def inject_session(page):
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

def record_v1_interactive(browser, output_dir):
    print("[*] Recording Interactive Video 1 with Visible Cursor & Meta Integration...")
    v_dir = os.path.join(output_dir, "minute_v1_cursor")
    os.makedirs(v_dir, exist_ok=True)
    context = browser.new_context(
        record_video_dir=v_dir,
        record_video_size={"width": 1920, "height": 1080},
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    setup_interception(page)
    inject_session(page)

    # 1. Integrations Page (0s - 10s)
    page.goto("http://127.0.0.1:5173/integrations")
    inject_cursor(page)
    page.wait_for_timeout(2500)
    smooth_move(page, 600, 350, steps=20)
    page.wait_for_timeout(1000)

    # Open Connect Modal for Facebook Messenger
    fb_card = page.locator("h3:has-text('Facebook Messenger')").first
    if fb_card.is_visible():
        move_and_click(page, fb_card)
        page.wait_for_timeout(2000)

    # 2. Click Continue with Meta Business (10s - 18s)
    meta_btn = page.locator("button:has-text('Continue with Meta Business')").first
    if meta_btn.is_visible():
        move_and_click(page, meta_btn)
        page.wait_for_timeout(2500)

    # 3. Meta Asset Selector Screen (18s - 28s)
    inject_cursor(page)
    ig_tab = page.locator("button:has-text('Instagram')").first
    if ig_tab.is_visible():
        move_and_click(page, ig_tab)
        page.wait_for_timeout(1500)

    fb_tab = page.locator("button:has-text('Facebook')").first
    if fb_tab.is_visible():
        move_and_click(page, fb_tab)
        page.wait_for_timeout(1500)

    account_card = page.locator("text=AI Sales Commander Official Page").first
    if account_card.is_visible():
        move_and_click(page, account_card)
        page.wait_for_timeout(1200)

    connect_btn = page.locator("button:has-text('Connect Selected Channel')").first
    if connect_btn.is_visible():
        move_and_click(page, connect_btn)
        page.wait_for_timeout(2500)

    # 4. Now on Integrations with connected channels (28s - 34s)
    inject_cursor(page)
    smooth_move(page, 900, 450, steps=20)
    page.wait_for_timeout(2000)

    # 5. Navigate to Messages (Unified Inbox) (34s - 52s)
    page.goto("http://127.0.0.1:5173/messages")
    inject_cursor(page)
    page.wait_for_timeout(2500)

    conv1 = page.locator("text=Sarah Connor").first
    if conv1.is_visible():
        move_and_click(page, conv1)
        page.wait_for_timeout(2000)

    msg_input = page.locator("input[placeholder*='message' i]").first
    if msg_input.is_visible():
        move_and_click(page, msg_input)
        msg_input.type("Hello Sarah! Our silk evening dress fits true to size. We have reserved one in Medium for you.", delay=35)
        page.wait_for_timeout(1000)
        send_btn = page.locator("button[aria-label='Send Message']").first
        if send_btn.is_visible():
            move_and_click(page, send_btn)
            page.wait_for_timeout(2500)

    conv3 = page.locator("text=Elena Rostova").first
    if conv3.is_visible():
        move_and_click(page, conv3)
        page.wait_for_timeout(2500)

    # 6. Navigate to Social Media (Comments & Triage) (52s - 63s)
    page.goto("http://127.0.0.1:5173/social")
    inject_cursor(page)
    page.wait_for_timeout(2500)

    comments_tab = page.locator("button:has-text('Comments & Triage')").first
    if comments_tab.is_visible():
        move_and_click(page, comments_tab)
        page.wait_for_timeout(2500)
        smooth_move(page, 750, 400, steps=20)
        page.wait_for_timeout(3500)

    v_path = page.video.path()
    context.close()
    print(f"[+] Interactive Video 1 recorded: {v_path}")
    return v_path

def record_v2_interactive(browser, output_dir):
    print("[*] Recording Interactive Video 2: Ads & Leads with Visible Cursor...")
    v_dir = os.path.join(output_dir, "minute_v2_cursor")
    os.makedirs(v_dir, exist_ok=True)
    context = browser.new_context(
        record_video_dir=v_dir,
        record_video_size={"width": 1920, "height": 1080},
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    setup_interception(page)
    inject_session(page)

    # 1. Reports & Marketing API (0s - 26s)
    page.goto("http://127.0.0.1:5173/reports")
    inject_cursor(page)
    page.wait_for_timeout(3000)
    smooth_move(page, 450, 250, steps=25)
    page.wait_for_timeout(2000)
    smooth_move(page, 850, 250, steps=25)
    page.wait_for_timeout(2000)
    page.mouse.wheel(0, 350)
    page.wait_for_timeout(3000)
    smooth_move(page, 600, 600, steps=20)
    page.wait_for_timeout(3000)
    page.mouse.wheel(0, -350)
    page.wait_for_timeout(2500)

    # 2. Deals & CRM Leads (26s - 54s)
    page.goto("http://127.0.0.1:5173/deals")
    inject_cursor(page)
    page.wait_for_timeout(3000)
    smooth_move(page, 350, 350, steps=25)
    page.wait_for_timeout(2500)
    lead_card = page.locator("text=Sarah Connor").first
    if lead_card.is_visible():
        move_and_click(page, lead_card)
        page.wait_for_timeout(3000)
    smooth_move(page, 750, 450, steps=25)
    page.wait_for_timeout(3500)

    v_path = page.video.path()
    context.close()
    print(f"[+] Interactive Video 2 recorded: {v_path}")
    return v_path

def record_v3_interactive(browser, output_dir):
    print("[*] Recording Interactive Video 3: Catalog & Media with Visible Cursor...")
    v_dir = os.path.join(output_dir, "minute_v3_cursor")
    os.makedirs(v_dir, exist_ok=True)
    context = browser.new_context(
        record_video_dir=v_dir,
        record_video_size={"width": 1920, "height": 1080},
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    setup_interception(page)
    inject_session(page)

    # 1. Products & Catalog (0s - 25s)
    page.goto("http://127.0.0.1:5173/products")
    inject_cursor(page)
    page.wait_for_timeout(3000)
    smooth_move(page, 450, 400, steps=25)
    page.wait_for_timeout(2500)
    smooth_move(page, 850, 400, steps=25)
    page.wait_for_timeout(2500)
    page.mouse.wheel(0, 350)
    page.wait_for_timeout(3000)
    page.mouse.wheel(0, -350)
    page.wait_for_timeout(2000)

    # 2. WhatsApp Settings (25s - 38s)
    page.goto("http://127.0.0.1:5173/integrations")
    inject_cursor(page)
    page.wait_for_timeout(2500)
    smooth_move(page, 850, 350, steps=25)
    page.wait_for_timeout(3000)

    # 3. Social Media & Video Publishing (38s - 52s)
    page.goto("http://127.0.0.1:5173/social")
    inject_cursor(page)
    page.wait_for_timeout(2500)
    feed_tab = page.locator("button:has-text('Post Feeds')").first
    if feed_tab.is_visible():
        move_and_click(page, feed_tab)
        page.wait_for_timeout(3500)

    v_path = page.video.path()
    context.close()
    print(f"[+] Interactive Video 3 recorded: {v_path}")
    return v_path

def main():
    base_dir = r"c:\Users\ARKAN STOER\Desktop\777"
    raw_dir = os.path.join(base_dir, "recordings")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True
        )
        record_v1_interactive(browser, raw_dir)
        record_v2_interactive(browser, raw_dir)
        record_v3_interactive(browser, raw_dir)
        browser.close()

    print("\n[SUCCESS] All interactive videos recorded with visible cursor and Meta integration!")

if __name__ == "__main__":
    main()
