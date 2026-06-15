#!/usr/bin/env python3
"""
Quick deployment verification script.
Tests key endpoints to ensure the backend is working correctly.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Your deployed backend URL
BASE_URL = "https://ai-sales-bot-api-production-412b.up.railway.app"

async def test_endpoint(session, endpoint, method="GET", data=None):
    """Test a single endpoint."""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            async with session.get(url) as response:
                status = response.status
                text = await response.text()
                return {"endpoint": endpoint, "status": status, "success": status < 400, "response": text[:200]}
        elif method == "POST":
            async with session.post(url, json=data) as response:
                status = response.status
                text = await response.text()
                return {"endpoint": endpoint, "status": status, "success": status < 400, "response": text[:200]}
    except Exception as e:
        return {"endpoint": endpoint, "status": "ERROR", "success": False, "error": str(e)}

async def main():
    """Run deployment tests."""
    print(f"🚀 Testing deployment at: {BASE_URL}")
    print(f"⏰ Started at: {datetime.now()}")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test basic endpoints
        tests = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/health/db", "GET"),
            ("/debug/config", "GET"),
        ]
        
        results = []
        for endpoint, method in tests:
            print(f"Testing {method} {endpoint}...")
            result = await test_endpoint(session, endpoint, method)
            results.append(result)
            
            if result["success"]:
                print(f"  ✅ {result['status']} - OK")
            else:
                print(f"  ❌ {result.get('status', 'ERROR')} - FAILED")
                if 'error' in result:
                    print(f"     Error: {result['error']}")
                else:
                    print(f"     Response: {result['response']}")
            print()
    
    print("=" * 60)
    print("📊 SUMMARY:")
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Deployment looks good!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    print(f"⏰ Completed at: {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(main())
