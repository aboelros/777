import os
from playwright.sync_api import sync_playwright

OVERLAYS = [
    {
        "filename": "overlay_v1_top.png",
        "title": "AI Sales Commander — Omnichannel Customer Care & Messaging",
        "subtitle": "Meta App Review Demonstration | App ID: 2387724232044213",
        "badge": "PERMISSIONS: pages_messaging • instagram_manage_messages • whatsapp_business_messaging • pages_show_list • pages_manage_metadata",
        "color": "#0ea5e9"
    },
    {
        "filename": "overlay_v2_top.png",
        "title": "AI Sales Commander — Meta Ads, Marketing API & Leads Retrieval",
        "subtitle": "Meta App Review Demonstration | App ID: 2387724232044213",
        "badge": "PERMISSIONS: leads_retrieval • ads_read • ads_management • Marketing API Access Tier • pages_manage_ads",
        "color": "#8b5cf6"
    },
    {
        "filename": "overlay_v3_top.png",
        "title": "AI Sales Commander — Meta Commerce Catalog & Media Publishing",
        "subtitle": "Meta App Review Demonstration | App ID: 2387724232044213",
        "badge": "PERMISSIONS: catalog_management • business_management • whatsapp_business_management • publish_video • Live Video API",
        "color": "#10b981"
    }
]

def generate_overlays():
    os.makedirs("meta_review_videos/overlays", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True
        )
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        for item in OVERLAYS:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
                * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
                body {{
                    width: 1920px;
                    height: 1080px;
                    background: transparent;
                    position: relative;
                    overflow: hidden;
                }}
                .header-container {{
                    position: absolute;
                    top: 20px;
                    left: 28px;
                    right: 28px;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }}
                .top-bar {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background: rgba(15, 23, 42, 0.92);
                    backdrop-filter: blur(16px);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    padding: 12px 24px;
                    border-radius: 14px;
                    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.6);
                }}
                .title-area {{ display: flex; flex-direction: column; }}
                .main-title {{
                    font-size: 18px;
                    font-weight: 700;
                    color: #ffffff;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                .meta-tag {{
                    background: {item['color']};
                    color: #ffffff;
                    font-size: 11px;
                    font-weight: 800;
                    padding: 3px 8px;
                    border-radius: 6px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .subtitle {{
                    font-size: 12px;
                    color: #94a3b8;
                    margin-top: 3px;
                }}
                .review-status {{
                    background: rgba(16, 185, 129, 0.15);
                    border: 1px solid rgba(16, 185, 129, 0.4);
                    color: #34d399;
                    font-size: 12px;
                    font-weight: 600;
                    padding: 5px 14px;
                    border-radius: 9999px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }}
                .review-status::before {{
                    content: "";
                    width: 7px;
                    height: 7px;
                    border-radius: 50%;
                    background: #34d399;
                    box-shadow: 0 0 8px #34d399;
                }}
                .perm-bar {{
                    background: rgba(15, 23, 42, 0.88);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    padding: 8px 18px;
                    border-radius: 10px;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    align-self: flex-start;
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
                }}
                .perm-badge {{
                    color: #cbd5e1;
                    font-size: 11px;
                    font-weight: 600;
                    letter-spacing: 0.3px;
                }}
            </style>
            </head>
            <body>
                <div class="header-container">
                    <div class="top-bar">
                        <div class="title-area">
                            <div class="main-title">
                                <span class="meta-tag">Meta App Review</span>
                                <span>{item['title']}</span>
                            </div>
                            <div class="subtitle">{item['subtitle']}</div>
                        </div>
                        <div class="review-status">Verified Production Flow</div>
                    </div>
                    <div class="perm-bar">
                        <div class="perm-badge">{item['badge']}</div>
                    </div>
                </div>
            </body>
            </html>
            """
            page.set_content(html)
            out_file = os.path.join("meta_review_videos/overlays", item["filename"])
            page.screenshot(path=out_file, omit_background=True)
            print(f"[+] Created header overlay: {out_file}")

        browser.close()

if __name__ == "__main__":
    generate_overlays()
