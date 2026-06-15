"""
Test script to verify WhatsApp Baileys integration.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from app.services.integrations.whatsapp_baileys import WhatsAppBaileysService
        print("✅ WhatsAppBaileysService imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import WhatsAppBaileysService: {e}")
        return False
    
    try:
        from app.services.whatsapp_gateway_client import WhatsAppGatewayClient
        print("✅ WhatsAppGatewayClient imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import WhatsAppGatewayClient: {e}")
        return False
    
    return True


def test_service_instantiation():
    """Test that services can be instantiated."""
    print("\nTesting service instantiation...")
    
    try:
        from app.services.integrations.whatsapp_baileys import WhatsAppBaileysService
        
        # Test without session_id
        service = WhatsAppBaileysService()
        print("✅ WhatsAppBaileysService instantiated without session_id")
        
        # Test with session_id
        service_with_session = WhatsAppBaileysService(session_id="test-session-123")
        assert service_with_session.session_id == "test-session-123"
        print("✅ WhatsAppBaileysService instantiated with session_id")
        
        return True
    except Exception as e:
        print(f"❌ Failed to instantiate service: {e}")
        return False


def test_webhook_parsing():
    """Test webhook parsing logic."""
    print("\nTesting webhook parsing...")
    
    try:
        from app.services.integrations.whatsapp_baileys import WhatsAppBaileysService
        
        service = WhatsAppBaileysService()
        
        # Test with valid Baileys webhook data
        test_webhook = {
            "message": {
                "key": {
                    "id": "msg123",
                    "remoteJid": "1234567890@s.whatsapp.net"
                },
                "messageTimestamp": 1234567890,
                "pushName": "Test User",
                "message": {
                    "conversation": "Hello, this is a test message"
                }
            }
        }
        
        parsed = service.parse_webhook(test_webhook)
        
        assert parsed is not None, "Parsing returned None"
        assert parsed["message_id"] == "msg123", "Message ID mismatch"
        assert parsed["from"] == "1234567890", "Sender mismatch"
        assert parsed["text"] == "Hello, this is a test message", "Text mismatch"
        assert parsed["contact"]["name"] == "Test User", "Contact name mismatch"
        
        print("✅ Webhook parsing works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Webhook parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("WhatsApp Baileys Integration Verification")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_service_instantiation,
        test_webhook_parsing
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed!")
        print("=" * 60)
        return 0
    else:
        print(f"❌ {results.count(False)} test(s) failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
