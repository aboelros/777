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
        "config": {
            "page_name": "AI Sales Commander Official Store",
            "page_id": "10029384819"
        },
        "created_at": "2026-01-10T12:00:00Z"
    },
    {
        "id": "meta-ig-1",
        "provider": "instagram",
        "status": "connected",
        "config": {
            "instagram_username": "aisalescommander_official",
            "page_id": "10029384819",
            "instagram_business_account_id": "1784140029384819"
        },
        "created_at": "2026-01-10T12:00:00Z"
    },
    {
        "id": "meta-wa-1",
        "provider": "whatsapp",
        "status": "connected",
        "config": {
            "phone_number": "+1 (555) 019-2834",
            "phone_number_id": "109283746",
            "waba_id": "987654321098"
        },
        "created_at": "2026-01-10T12:00:00Z"
    },
    {
        "id": "shopify-1",
        "provider": "shopify",
        "status": "connected",
        "config": {
            "shop_name": "aisales-store.myshopify.com"
        },
        "created_at": "2026-01-10T12:00:00Z"
    }
]

MOCK_CONVERSATIONS = [
    {
        "id": "conv-1",
        "customer_name": "Sarah Connor",
        "customer_email": "sarah.c@example.com",
        "channel": "instagram",
        "last_message": "Is this evening dress available in size Medium?",
        "unread_count": 1
    },
    {
        "id": "conv-2",
        "customer_name": "David Miller",
        "customer_email": "david.m@example.com",
        "channel": "facebook",
        "last_message": "Hello, do you offer express delivery to London?",
        "unread_count": 0
    },
    {
        "id": "conv-3",
        "customer_name": "Elena Rostova",
        "customer_email": "elena.r@example.com",
        "channel": "whatsapp",
        "last_message": "Could you send me the tracking link for order #8492?",
        "unread_count": 2
    }
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

def record_video_messaging(browser, output_dir):
    print("[*] Recording Video 1: Omnichannel Messaging & Social Customer Care...")
    v_dir = os.path.join(output_dir, "raw_v1")
    os.makedirs(v_dir, exist_ok=True)
    context = browser.new_context(
        record_video_dir=v_dir,
        record_video_size={"width": 1920, "height": 1080},
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    setup_interception(page)
    inject_session(page)

    # 1. Integrations overview
    page.goto("http://127.0.0.1:5173/integrations")
    page.wait_for_timeout(3500)
    page.mouse.wheel(0, 300)
    page.wait_for_timeout(2000)
    page.mouse.wheel(0, -300)
    page.wait_for_timeout(1500)

    # 2. Unified Messages
    page.goto("http://127.0.0.1:5173/messages")
    page.wait_for_timeout(3500)
    
    # Click Sarah Connor (Instagram)
    conv1 = page.locator("text=Sarah Connor").first
    if conv1.is_visible():
        conv1.click()
        page.wait_for_timeout(2000)

    # Type reply
    msg_input = page.locator("input[placeholder*='message' i]").first
    if msg_input.is_visible():
        msg_input.click()
        msg_input.type("Hello Sarah! Sizing is true to size. We have reserved one in Medium for you.", delay=30)
        page.wait_for_timeout(1000)
        send_btn = page.locator("button[aria-label='Send Message']").first
        if send_btn.is_visible():
            send_btn.click()
            page.wait_for_timeout(2000)

    # Click Elena Rostova (WhatsApp)
    conv3 = page.locator("text=Elena Rostova").first
    if conv3.is_visible():
        conv3.click()
        page.wait_for_timeout(2500)

    # Click David Miller (Facebook)
    conv2 = page.locator("text=David Miller").first
    if conv2.is_visible():
        conv2.click()
        page.wait_for_timeout(2500)

    # 3. Social Media Moderation
    page.goto("http://127.0.0.1:5173/social")
    page.wait_for_timeout(3000)
    comments_tab = page.locator("button:has-text('Comments & Triage')").first
    if comments_tab.is_visible():
        comments_tab.click()
        page.wait_for_timeout(3000)
        page.mouse.wheel(0, 250)
        page.wait_for_timeout(2000)

    page.wait_for_timeout(2000)
    video_path = page.video.path()
    context.close()
    print(f"[+] Video 1 recorded: {video_path}")
    return video_path

def record_video_ads_leads(browser, output_dir):
    print("[*] Recording Video 2: Meta Ads, Analytics & Lead Ads Retrieval...")
    v_dir = os.path.join(output_dir, "raw_v2")
    os.makedirs(v_dir, exist_ok=True)
    context = browser.new_context(
        record_video_dir=v_dir,
        record_video_size={"width": 1920, "height": 1080},
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    setup_interception(page)
    inject_session(page)

    # 1. Reports & Analytics
    page.goto("http://127.0.0.1:5173/reports")
    page.wait_for_timeout(4000)
    page.mouse.wheel(0, 350)
    page.wait_for_timeout(2500)
    page.mouse.wheel(0, -350)
    page.wait_for_timeout(2000)

    # 2. CRM & Deals (Leads Retrieval)
    page.goto("http://127.0.0.1:5173/deals")
    page.wait_for_timeout(4000)
    page.mouse.wheel(0, 300)
    page.wait_for_timeout(2000)
    page.mouse.wheel(0, -300)
    page.wait_for_timeout(2000)

    video_path = page.video.path()
    context.close()
    print(f"[+] Video 2 recorded: {video_path}")
    return video_path

def record_video_catalog_media(browser, output_dir):
    print("[*] Recording Video 3: Commerce Catalog, WABA & Media Management...")
    v_dir = os.path.join(output_dir, "raw_v3")
    os.makedirs(v_dir, exist_ok=True)
    context = browser.new_context(
        record_video_dir=v_dir,
        record_video_size={"width": 1920, "height": 1080},
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    setup_interception(page)
    inject_session(page)

    # 1. Products / Catalog
    page.goto("http://127.0.0.1:5173/products")
    page.wait_for_timeout(4000)
    page.mouse.wheel(0, 350)
    page.wait_for_timeout(2500)
    page.mouse.wheel(0, -350)
    page.wait_for_timeout(2000)

    # 2. Social Feeds & Media
    page.goto("http://127.0.0.1:5173/social")
    page.wait_for_timeout(3500)
    feed_tab = page.locator("button:has-text('Post Feeds')").first
    if feed_tab.is_visible():
        feed_tab.click()
        page.wait_for_timeout(3000)

    video_path = page.video.path()
    context.close()
    print(f"[+] Video 3 recorded: {video_path}")
    return video_path

def main():
    base_dir = r"c:\Users\ARKAN STOER\Desktop\777"
    raw_dir = os.path.join(base_dir, "recordings")
    os.makedirs(raw_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True
        )
        v1 = record_video_messaging(browser, raw_dir)
        v2 = record_video_ads_leads(browser, raw_dir)
        v3 = record_video_catalog_media(browser, raw_dir)
        browser.close()

    print("\n[SUCCESS] All 3 raw video clips recorded successfully!")

if __name__ == "__main__":
    main()
