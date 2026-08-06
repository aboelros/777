
import traceback
try:
    import google.generativeai as genai
    print("✅ genai imported")
    try:
        print(f"genai version: {genai.__version__}")
    except:
        pass
        
    try:
        from google.ai import generativelanguage as glm
        print("✅ google.ai.generativelanguage imported as glm")
        
        # Try to use glm types
        t = glm.Type.STRING
        print(f"✅ glm.Type.STRING available: {t}")
        
        s = glm.Schema(type=glm.Type.STRING)
        print(f"✅ glm.Schema available: {s}")
        
    except ImportError:
        print("❌ Could not import google.ai.generativelanguage")
    except Exception as e:
        print(f"❌ Error using glm: {e}")
        traceback.print_exc()

except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()
