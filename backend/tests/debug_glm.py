
import traceback
from google.ai import generativelanguage as glm

try:
    print("Testing glm.Schema constructor...")
    
    # Test 1: Using type_
    try:
        s1 = glm.Schema(type_=glm.Type.STRING)
        print(f"✅ glm.Schema(type_=...) worked: {s1}")
    except Exception as e:
        print(f"❌ glm.Schema(type_=...) failed: {e}")

    # Test 2: Using type
    try:
        s2 = glm.Schema(type=glm.Type.STRING)
        print(f"✅ glm.Schema(type=...) worked: {s2}")
    except Exception as e:
        print(f"❌ glm.Schema(type=...) failed: {e}")
        
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    traceback.print_exc()
