import time
import urllib.request
from datetime import datetime

# URLs to ping (from your render.yaml)
URLS = [
    "https://ai-sales-bot-api-vdr6.onrender.com/health",
    "https://ai-sales-bot-whatsapp-vdr6.onrender.com/health"
]

PING_INTERVAL = 600  # 10 minutes in seconds

def ping_urls():
    for url in URLS:
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Pinging {url}...")
            # Using a simple GET request
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=10)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Success! Status: {response.getcode()}")
        except Exception as e:
            # We catch exceptions so that a failure on one doesn't stop the script or crash it
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to ping {url}: {e}")
            # Try falling back to root URL if /health is not found
            fallback_url = url.replace("/health", "")
            try:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Trying fallback: {fallback_url}...")
                req = urllib.request.Request(fallback_url, headers={'User-Agent': 'Mozilla/5.0'})
                response = urllib.request.urlopen(req, timeout=10)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fallback Success! Status: {response.getcode()}")
            except Exception as fallback_e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fallback Failed: {fallback_e}")

if __name__ == "__main__":
    print(f"Starting keep-alive script. Pinging every {PING_INTERVAL // 60} minutes.")
    print("Press Ctrl+C to stop.")
    
    # Run immediately on startup
    ping_urls()
    
    # Loop forever
    while True:
        try:
            time.sleep(PING_INTERVAL)
            ping_urls()
        except KeyboardInterrupt:
            print("\nKeep-alive script stopped by user.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(60) # Wait a bit before retrying if there's a serious error
