
import os
import sys

def check_env():
    print("="*50)
    print("🔍 DEBUG: Environment Variable Check")
    print("="*50)
    
    # Check specific keys
    keys_to_check = [
        "FACEBOOK_APP_ID", 
        "FACEBOOK_APP_SECRET", 
        "META_APP_ID", 
        "META_APP_SECRET"
    ]
    
    found_any = False
    for key in keys_to_check:
        value = os.environ.get(key)
        if value:
            masked = value[:4] + "*" * (len(value)-4) if len(value) > 4 else "***"
            print(f"✅ {key}: FOUND (Length: {len(value)}) | Preview: {masked}")
            found_any = True
        else:
            print(f"❌ {key}: NOT FOUND or EMPTY")
            
    print("-" * 50)
    if not found_any:
        print("⚠️  CRITICAL: No Meta/Facebook App keys found in environment!")
    else:
        print("ℹ️  At least one key was found.")
    print("="*50)

if __name__ == "__main__":
    check_env()
