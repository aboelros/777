import os
import sys
import asyncio
from typing import Dict, Any, List
import httpx

API_VERSION = "v19.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

async def run_test_calls(
    access_token: str,
    page_id: str = "me",
    ad_account_id: str = "",
    ig_user_id: str = "",
    waba_id: str = "",
    phone_number_id: str = ""
) -> None:
    """Execute Graph API test calls to fulfill Meta App Review requirements."""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    test_endpoints: List[Dict[str, Any]] = [
        {
            "permission": "pages_show_list",
            "url": f"{BASE_URL}/me/accounts",
            "method": "GET"
        },
        {
            "permission": "pages_read_engagement",
            "url": f"{BASE_URL}/{page_id}?fields=id,name,fan_count,verification_status",
            "method": "GET"
        },
        {
            "permission": "pages_manage_metadata",
            "url": f"{BASE_URL}/{page_id}/subscribed_apps",
            "method": "GET"
        },
        {
            "permission": "pages_messaging",
            "url": f"{BASE_URL}/{page_id}/conversations",
            "method": "GET"
        },
        {
            "permission": "business_management",
            "url": f"{BASE_URL}/me/businesses",
            "method": "GET"
        }
    ]

    if ig_user_id:
        test_endpoints.extend([
            {
                "permission": "instagram_basic & instagram_business_basic",
                "url": f"{BASE_URL}/{ig_user_id}?fields=id,username,profile_picture_url",
                "method": "GET"
            },
            {
                "permission": "instagram_manage_comments",
                "url": f"{BASE_URL}/{ig_user_id}/media?fields=id,caption,comments_count",
                "method": "GET"
            }
        ])

    if ad_account_id:
        ad_acc = ad_account_id if ad_account_id.startswith("act_") else f"act_{ad_account_id}"
        test_endpoints.extend([
            {
                "permission": "ads_read & Marketing API",
                "url": f"{BASE_URL}/{ad_acc}/campaigns?fields=id,name,status",
                "method": "GET"
            },
            {
                "permission": "pages_manage_ads & ads_management",
                "url": f"{BASE_URL}/{ad_acc}/insights?fields=impressions,spend",
                "method": "GET"
            }
        ])

    if waba_id:
        test_endpoints.append({
            "permission": "whatsapp_business_management",
            "url": f"{BASE_URL}/{waba_id}/message_templates",
            "method": "GET"
        })

    if phone_number_id:
        test_endpoints.append({
            "permission": "whatsapp_business_messaging",
            "url": f"{BASE_URL}/{phone_number_id}?fields=verified_name,display_phone_number",
            "method": "GET"
        })

    async with httpx.AsyncClient(timeout=15.0) as client:
        print(f"[*] Starting Meta Graph API test calls for App Review verification...\n")
        passed = 0
        failed = 0

        for test in test_endpoints:
            perm = test["permission"]
            url = test["url"]
            print(f"[*] Testing [{perm}] -> {url}...")
            try:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    print(f"    [+] SUCCESS (HTTP 200)")
                    passed += 1
                else:
                    print(f"    [-] HTTP {resp.status_code}: {resp.text[:120]}")
                    failed += 1
            except Exception as exc:
                print(f"    [!] Error: {exc}")
                failed += 1

        print(f"\n==========================================")
        print(f"Summary: {passed} passed, {failed} failed")
        print(f"Meta's telemetry will register successful calls for your App ID within a few minutes.")
        print(f"==========================================\n")

if __name__ == "__main__":
    token = os.getenv("META_ACCESS_TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not token:
        print("Usage: python scripts/meta_app_review_test_calls.py <ACCESS_TOKEN> [PAGE_ID] [AD_ACCOUNT_ID]")
        print("Or set META_ACCESS_TOKEN environment variable.")
        sys.exit(1)

    p_id = sys.argv[2] if len(sys.argv) > 2 else "me"
    ad_id = sys.argv[3] if len(sys.argv) > 3 else ""
    asyncio.run(run_test_calls(access_token=token, page_id=p_id, ad_account_id=ad_id))
