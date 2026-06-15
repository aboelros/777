import requests
import json
import time
import random
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your backend port is different
PROJECT_ID = "YOUR_PROJECT_ID_HERE" # User will need to replace this or we can try to fetch it
WEBHOOK_PATH = "/api/v1/webhooks/shopify"

def generate_mock_shopify_order():
    order_id = random.randint(10000, 99999)
    total = round(random.uniform(50.0, 500.0), 2)
    
    return {
        "id": order_id,
        "email": f"customer_{random.randint(1, 100)}@example.com",
        "created_at": datetime.now().isoformat(),
        "currency": "USD",
        "total_price": str(total),
        "line_items": [
            {
                "id": random.randint(100000, 999999),
                "title": random.choice(["Premium T-Shirt", "Wireless Headphones", "Smart Watch", "Leather Wallet"]),
                "quantity": random.randint(1, 3),
                "price": str(round(total / random.randint(1, 3), 2))
            }
        ],
        "customer": {
            "first_name": random.choice(["John", "Jane", "Alice", "Bob"]),
            "last_name": random.choice(["Doe", "Smith", "Johnson", "Brown"]),
            "email": f"customer_{random.randint(1, 100)}@example.com"
        }
    }

def simulate_webhook():
    print(f"🚀 Sending mock webhooks to {BASE_URL}...")
    
    # 1. Simulate Shopify Order Created
    payload = generate_mock_shopify_order()
    headers = {
        "X-Shopify-Topic": "orders/create",
        "X-Shopify-Hmac-Sha256": "mock_signature",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}{WEBHOOK_PATH}", json=payload, headers=headers)
        print(f"✅ Sent Order Webhook: {response.status_code}")
        print(f"   Payload ID: {payload['id']}")
    except Exception as e:
        print(f"❌ Failed to send webhook: {e}")

    # 2. Simulate Incoming Message (WhatsApp/Meta) with Sentiment
    # We'll calculate a signature or skip if validation is loose in dev
    
    print("\n-------- Simulating Sentiment Messages --------")
    
    scenarios = [
        {"text": "I love this product! It's amazing and perfect.", "expected": "positive"},
        {"text": "My order is broken and I hate it. Terrible service.", "expected": "negative"},
        {"text": "PLEASE HELP ASAP! EMERGENCY! My account is stuck.", "expected": "urgent"},
        {"text": "Just checking if you are open today.", "expected": "neutral"}
    ]
    
    # Using the generic webhook endpoint or a specific adapter endpoint
    # For now, let's assume we hit the Meta/WhatsApp endpoint if available, 
    # or the general logs will catch it if we send to a demo endpoint.
    
    # Since we don't have a generic 'ingest message' endpoint without signatures for Meta,
    # we will focus on the fact that the USER can see these logs if we send them as ANY webhook.
    # But to test Sentiment, we need the WebhookProcessor to run.
    # The WebhookGateway authenticates mostly via URL tokens or Signatures.
    
    # Let's try to hit the 'whatsapp' webhook. 
    # Usually requires a verify_token challenge first, or signature.
    # If we want to force-feed a message, we might need a dev-only endpoint or rely on the implementation 
    # allowing loose checks in debug mode.
    
    # Alternatively, we can just print instructions for the user to send those texts to the actual bot.
    
    print("To verify Sentiment Badges, send these messages to your bot:")
    for s in scenarios:
        print(f"   [{s['expected'].upper()}] -> \"{s['text']}\"")
        
    print("\nTo see incoming payloads, check the 'Live Logs' in the Integrations page.")

if __name__ == "__main__":
    simulate_webhook()
