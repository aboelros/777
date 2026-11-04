"""
Test script to verify WhatsApp Baileys integration.
"""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    from app.services.integrations.whatsapp_baileys import WhatsAppBaileysService
    from app.services.whatsapp_gateway_client import WhatsAppGatewayClient
    print("✅ WhatsAppBaileysService imported successfully")
    print("✅ WhatsAppGatewayClient imported successfully")


def test_service_instantiation():
    """Test that services can be instantiated."""
    print("\nTesting service instantiation...")
    from app.services.integrations.whatsapp_baileys import WhatsAppBaileysService
    
    # Test without session_id
    service = WhatsAppBaileysService()
    print("✅ WhatsAppBaileysService instantiated without session_id")
    
    # Test with session_id
    service_with_session = WhatsAppBaileysService(session_id="test-session-123")
    assert service_with_session.session_id == "test-session-123"
    print("✅ WhatsAppBaileysService instantiated with session_id")


def test_webhook_parsing():
    """Test webhook parsing logic."""
    print("\nTesting webhook parsing...")
    from app.services.integrations.whatsapp_baileys import WhatsAppBaileysService
    
    service = WhatsAppBaileysService()
    
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
    
    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    if failed == 0:
        print("✅ All tests passed!")
        print("=" * 60)
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
