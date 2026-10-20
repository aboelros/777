import os
import time
from playwright.sync_api import sync_playwright

def record_video_1():
    os.makedirs("recordings", exist_ok=True)
    os.makedirs("meta_review_videos", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True
        )
        context = browser.new_context(
            record_video_dir="recordings",
            record_video_size={"width": 1920, "height": 1080},
            viewport={"width": 1920, "height": 1080}
        )

        # Setup local storage with project and auth
        page = context.new_page()
        page.goto("http://127.0.0.1:5173/")
        page.evaluate("""() => {
            localStorage.setItem('project-storage', JSON.stringify({
                state: {
                    currentProject: {
                        id: 'c1f7a0b2-4d8e-4b6a-9a8f-2e3d4c5b6a7b',
                        name: 'AI Sales Commander Demo Store'
                    },
                    projects: [
                        {
                            id: 'c1f7a0b2-4d8e-4b6a-9a8f-2e3d4c5b6a7b',
                            name: 'AI Sales Commander Demo Store'
                        }
                    ]
                }
            }));
            localStorage.setItem('auth-storage', JSON.stringify({
                state: {
                    user: { name: 'Meta Reviewer', email: 'reviewer@example.com' },
                    isAuthenticated: true
                }
            }));
        }""")

        # 1. Start at Integrations
        page.goto("http://127.0.0.1:5173/integrations")
        page.wait_for_timeout(3000)

        # Scroll down smoothly
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(2000)
        page.mouse.wheel(0, -400)
        page.wait_for_timeout(1500)

        # 2. Navigate to Messages (Unified Inbox)
        page.goto("http://127.0.0.1:5173/messages")
        page.wait_for_timeout(3000)

        # Click on conversation items
        items = page.locator(".cursor-pointer")
        count = items.count()
        if count > 0:
            items.first.click()
            page.wait_for_timeout(2000)

        # Type message in chat input
        textarea = page.locator("textarea, input[placeholder*='message' i], input[placeholder*='type' i]").first
        if textarea.is_visible():
            textarea.click()
            textarea.type("Hello Sarah! Thanks for contacting AI Sales Commander. Yes, express delivery is available worldwide.", delay=40)
            page.wait_for_timeout(1500)
            send_btn = page.locator("button:has-text('Send'), button:has([data-lucide='send']), button:has([class*='Send'])").first
            if send_btn.is_visible():
                send_btn.click()
                page.wait_for_timeout(2000)

        # Select second conversation
        if count > 1:
            items.nth(1).click()
            page.wait_for_timeout(2500)

        # 3. Navigate to Social Media (/social)
        page.goto("http://127.0.0.1:5173/social")
        page.wait_for_timeout(3000)

        # Click Tabs (Post Feeds, Comments)
        feed_tab = page.locator("button:has-text('Post Feeds'), button:has-text('Feed')").first
        if feed_tab.is_visible():
            feed_tab.click()
            page.wait_for_timeout(2500)
            page.mouse.wheel(0, 300)
            page.wait_for_timeout(1500)

        comments_tab = page.locator("button:has-text('Comments'), button:has-text('Triage')").first
        if comments_tab.is_visible():
            comments_tab.click()
            page.wait_for_timeout(2500)

        page.wait_for_timeout(2000)
        video_path = page.video.path()
        context.close()
        browser.close()
        print(f"Recorded Video 1 raw webm: {video_path}")
        return video_path

if __name__ == "__main__":
    record_video_1()
