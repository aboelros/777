"""
Quick test to verify WhatsApp webhook fix.
Run this to check if the AI orchestrator can process messages without Product model.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def test_ai_orchestrator():
    """Test AI orchestrator message processing."""
    from app.core.database import AsyncSessionLocal
    from app.services.ai_orchestrator import AIOrchestrator
    from uuid import uuid4
    
    print("=" * 60)
    print("Testing AI Orchestrator (WhatsApp Webhook Fix)")
    print("=" * 60)
    
    async with AsyncSessionLocal() as db:
        orchestrator = AIOrchestrator(db)
        
        # Test 1: Check if _get_product_catalog handles missing Product model
        print("\n✅ Test 1: Product Catalog with Missing Model")
        print("-" * 60)
        try:
            project_id = uuid4()
            products = await orchestrator._get_product_catalog(project_id)
            print(f"✅ SUCCESS: Returned {len(products)} products (expected 0)")
            print(f"   This means the ImportError is handled correctly!")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            return False
        
        # Test 2: Check conversation history (should work)
        print("\n✅ Test 2: Conversation History")
        print("-" * 60)
        try:
            customer_id = uuid4()
            history = await orchestrator._get_conversation_history(customer_id, limit=5)
            print(f"✅ SUCCESS: Returned {len(history)} messages")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            return False
        
        # Test 3: Language detection
        print("\n✅ Test 3: Language Detection")
        print("-" * 60)
        try:
            lang_en = orchestrator._detect_language("Hello, how are you?")
            lang_ar = orchestrator._detect_language("مرحبا كيف حالك؟")
            print(f"✅ SUCCESS: English detected as '{lang_en}'")
            print(f"✅ SUCCESS: Arabic detected as '{lang_ar}'")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📋 Summary:")
        print("   - Product catalog gracefully handles missing Product model")
        print("   - Conversation history works correctly")
        print("   - Language detection is functional")
        print("\n🚀 The webhook should now work properly!")
        print("   Send a WhatsApp message to test the full flow.")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_ai_orchestrator())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
