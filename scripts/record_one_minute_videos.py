import os
import json
import time
from playwright.sync_api import sync_playwright

MOCK_PROJECT = {
    "id": "c1f7a0b2-4d8e-4b6a-9a8f-2e3d4c5b6a7b",
    "name": "AI Sales Commander Demo Store",
    "domain": "store.example.com",
    "currency": "USD"
}

MOCK_INTEGRATIONS = [
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

def setup_interception(page):
    def route_handler(route):
        url = route.request.url
        if "/api/v1/projects" in url and route.request.method == "GET":
            route.fulfill(status=200, content_type="application/json", body=json.dumps([MOCK_PROJECT]))
        elif "/api/v1/integrations" in url:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(MOCK_INTEGRATIONS))
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

def record_v1_full(browser, output_dir):
    print("[*] Recording 1-Minute Video 1: Omnichannel Messaging (~66s)...")
    v_dir = os.path.join(output_dir, "minute_v1")
    os.makedirs(v_dir, exist_ok=True)
    context = browser.new_context(
        record_video_dir=v_dir,
        record_video_size={"width": 1920, "height": 1080},
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    setup_interception(page)
    inject_session(page)

    # 0s - 12s: Integrations Overview
    page.goto("http://127.0.0.1:5173/integrations")
    page.wait_for_timeout(4000)
    page.mouse.wheel(0, 350)
    page.wait_for_timeout(3500)
    page.mouse.wheel(0, -350)
    page.wait_for_timeout(3500)

    # 12s - 45s: Messages (Unified Inbox)
    page.goto("http://127.0.0.1:5173/messages")
    page.wait_for_timeout(4000)
    
    # Click Sarah Connor
    conv1 = page.locator("text=Sarah Connor").first
    if conv1.is_visible():
        conv1.click()
        page.wait_for_timeout(3500)

    # Type response
    msg_input = page.locator("input[placeholder*='message' i]").first
    if msg_input.is_visible():
        msg_input.click()
        msg_input.type("Hello Sarah! Our silk evening dress fits true to size. We have reserved one in Medium for you.", delay=45)
        page.wait_for_timeout(2000)
        send_btn = page.locator("button[aria-label='Send Message']").first
        if send_btn.is_visible():
            send_btn.click()
            page.wait_for_timeout(3500)

    # Switch to WhatsApp
    conv3 = page.locator("text=Elena Rostova").first
    if conv3.is_visible():
        conv3.click()
        page.wait_for_timeout(4500)

    # Switch to Messenger
    conv2 = page.locator("text=David Miller").first
    if conv2.is_visible():
        conv2.click()
        page.wait_for_timeout(4500)

    # 45s - 66s: Social Media Comments & Triage
    page.goto("http://127.0.0.1:5173/social")
    page.wait_for_timeout(4000)
    comments_tab = page.locator("button:has-text('Comments & Triage')").first
    if comments_tab.is_visible():
        comments_tab.click()
        page.wait_for_timeout(4500)
        page.mouse.wheel(0, 300)
        page.wait_for_timeout(4000)

    page.wait_for_timeout(3000)
    v_path = page.video.path()
    context.close()
    print(f"[+] Video 1 finished: {v_path}")
    return v_path

def record_v2_full(browser, output_dir):
    print("[*] Recording 1-Minute Video 2: Ads & Leads (~56s)...")
    v_dir = os.path.join(output_dir, "minute_v2")
    os.makedirs(v_dir, exist_ok=True)
    context = browser.new_context(
        record_video_dir=v_dir,
        record_video_size={"width": 1920, "height": 1080},
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    setup_interception(page)
    inject_session(page)

    # 0s - 28s: Reports & Marketing API
    page.goto("http://127.0.0.1:5173/reports")
    page.wait_for_timeout(5000)
    page.mouse.wheel(0, 350)
    page.wait_for_timeout(5000)
    page.mouse.wheel(0, 350)
    page.wait_for_timeout(5000)
    page.mouse.wheel(0, -700)
    page.wait_for_timeout(5000)

    # 28s - 56s: Deals & CRM Leads Retrieval
    page.goto("http://127.0.0.1:5173/deals")
    page.wait_for_timeout(5000)
    page.mouse.wheel(0, 350)
    page.wait_for_timeout(5000)
    page.mouse.wheel(0, -350)
    page.wait_for_timeout(5000)
    page.wait_for_timeout(6000)

    v_path = page.video.path()
    context.close()
    print(f"[+] Video 2 finished: {v_path}")
    return v_path

def record_v3_full(browser, output_dir):
    print("[*] Recording 1-Minute Video 3: Catalog & Media (~54s)...")
    v_dir = os.path.join(output_dir, "minute_v3")
    os.makedirs(v_dir, exist_ok=True)
    context = browser.new_context(
        record_video_dir=v_dir,
        record_video_size={"width": 1920, "height": 1080},
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    setup_interception(page)
    inject_session(page)

    # 0s - 26s: Commerce Products Catalog
    page.goto("http://127.0.0.1:5173/products")
    page.wait_for_timeout(5000)
    page.mouse.wheel(0, 350)
    page.wait_for_timeout(5000)
    page.mouse.wheel(0, 350)
    page.wait_for_timeout(5000)
    page.mouse.wheel(0, -700)
    page.wait_for_timeout(5000)

    # 26s - 40s: WhatsApp Business & Portfolio settings
    page.goto("http://127.0.0.1:5173/integrations")
    page.wait_for_timeout(5000)
    page.mouse.wheel(0, 300)
    page.wait_for_timeout(4000)

    # 40s - 54s: Social Feeds & Video Publishing
    page.goto("http://127.0.0.1:5173/social")
    page.wait_for_timeout(4000)
    feed_tab = page.locator("button:has-text('Post Feeds')").first
    if feed_tab.is_visible():
        feed_tab.click()
        page.wait_for_timeout(5000)
    page.wait_for_timeout(4000)

    v_path = page.video.path()
    context.close()
    print(f"[+] Video 3 finished: {v_path}")
    return v_path

def main():
    base_dir = r"c:\Users\ARKAN STOER\Desktop\777"
    raw_dir = os.path.join(base_dir, "recordings")
    os.makedirs(raw_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True
        )
        record_v1_full(browser, raw_dir)
        record_v2_full(browser, raw_dir)
        record_v3_full(browser, raw_dir)
        browser.close()

    print("\n[SUCCESS] All 3 one-minute raw video clips recorded successfully!")

if __name__ == "__main__":
    main()
