import asyncio
import sys
import os
import structlog

# Add backend directory to path
sys.path.append(os.getcwd())

from app.services.integrations.whatsapp_gateway_service import WhatsAppGatewayService

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ]
)

async def test_send():
    # REPLACE THESE WITH ACTUAL VALUES FROM YOUR DATABASE/LOGS
    BASE_URL = "https://wa-gateway.railway.app"  # Ensure this is correct
    SESSION_ID = "fff"  # From your logs
    TO_NUMBER = "201063200566@s.whatsapp.net"  # From your logs
    
    print(f"Testing WA-Gateway...")
    print(f"URL: {BASE_URL}")
    print(f"Session: {SESSION_ID}")
    print(f"To: {TO_NUMBER}")
    
    endpoints = [
        "/session/start",
        "/session/start?session=test",
        "/api/session/start",
        "/session/status",
        "/message/send-text"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        import httpx
        client = httpx.AsyncClient()
        
        url = f"{BASE_URL}{endpoint}"
        
        try:
            # Try GET first
            print("GET request:")
            resp = await client.get(url, follow_redirects=True)
            print(f"Status: {resp.status_code}")
            if resp.status_code != 404:
                print(f"FOUND! Response: {resp.text[:200]}...")
                
            # Try POST
            print("POST request:")
            resp = await client.post(url, json={}, follow_redirects=True)
            print(f"Status: {resp.status_code}")
            if resp.status_code != 404:
                print(f"FOUND! Response: {resp.text[:200]}...")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await client.aclose()
        
if __name__ == "__main__":
    asyncio.run(test_send())
