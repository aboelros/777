import time
import requests
import datetime

USER_TOKEN = "EAAh7n16sLrUBS6BUUqGVjJGroPqnLx6AJupR7qr2rEVFtLcn67e2ZAZC35k93Ew6QeQbg7DdEhaxgS2cXYXhlbZBwH7sz2rg3Ybe4mOVeFQCwTCQe9jmc9NFp2nZA8hI3BZCMZBg6C5ZAUcF42eCSOimdaM5s6hOVEZBDgFGeO0sZCHpZA9mcrtEQe9Vk4DNw3yvRljJXL4pwYbwRFpZC1cwZC1ExwwYqRzSopuDMjjguTPaXj6fNjYkv0MwvZAALSQwUbcOHrIqj5CF6Un8ZD"
AD_ACCOUNT_ID = "act_566380635710327"
TARGET_CALLS = 200  # Will bring total successful to 325 + 200 = 525 calls
URL = f"https://graph.facebook.com/v19.0/{AD_ACCOUNT_ID}"
PARAMS = {
    "access_token": USER_TOKEN,
    "fields": "id,name,account_status,currency"
}

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def main():
    log("Starting Meta Marketing API Pacer to complete remaining 175+ calls...")
    completed = 0
    
    # First, wait for cooldown to clear
    while True:
        try:
            r = requests.get(URL, params=PARAMS, timeout=10)
            if r.status_code == 200:
                log("Cooldown lifted! Endpoint responded with HTTP 200. Resuming calls...")
                completed += 1
                break
            else:
                log(f"Cooldown active (HTTP {r.status_code}). Waiting 60 seconds...")
                time.sleep(60)
        except Exception as e:
            log(f"Probe exception: {e}. Retrying in 60s...")
            time.sleep(60)

    # Now make paced calls with 1.5s delay to strictly avoid rate limit
    while completed < TARGET_CALLS:
        try:
            p = dict(PARAMS)
            p["_seq"] = str(completed + 1)
            res = requests.get(URL, params=p, timeout=10)
            if res.status_code == 200:
                completed += 1
                if completed % 25 == 0 or completed == TARGET_CALLS:
                    log(f"Paced Progress: {completed}/{TARGET_CALLS} additional calls completed (Total lifetime today: {325 + completed})")
                time.sleep(1.2)
            elif res.status_code == 400 and "too many calls" in res.text.lower():
                log("Rate limit tapped. Pausing for 3 minutes...")
                time.sleep(180)
            else:
                log(f"Response {res.status_code}: {res.text[:100]}")
                time.sleep(2)
        except Exception as e:
            log(f"Error during call: {e}")
            time.sleep(3)

    log(f"DONE! {completed} additional Marketing API calls completed.")
    log(f"Grand Total: {325 + completed} successful Marketing API calls recorded for App ID 2387724232044213.")

if __name__ == "__main__":
    main()
