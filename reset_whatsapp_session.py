"""
Automated WhatsApp Session Reset Script
Fixes "Bad MAC", "Failed to decrypt", and session encryption errors
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def reset_whatsapp_session():
    """Reset corrupted WhatsApp session."""
    from app.core.database import AsyncSessionLocal
    from app.db.models import Integration, IntegrationStatus
    from sqlalchemy import select
    from app.services.integrations.whatsapp_gateway_service import WhatsAppGatewayService
    from app.core.config import settings
    
    print("=" * 70)
    print("🔧 WhatsApp Session Reset Tool")
    print("=" * 70)
    print("\nThis will fix 'Bad MAC', 'Failed to decrypt', and encryption errors")
    print("\n⚠️  WARNING: This will disconnect your current WhatsApp session!")
    print("You will need to scan a new QR code to reconnect.\n")
    
    response = input("Do you want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Aborted by user")
        return False
    
    async with AsyncSessionLocal() as db:
        # Step 1: Find WhatsApp integrations
        print("\n" + "=" * 70)
        print("Step 1: Finding WhatsApp integrations...")
        print("=" * 70)
        
        result = await db.execute(
            select(Integration).where(Integration.provider == "whatsapp")
        )
        integrations = result.scalars().all()
        
        if not integrations:
            print("❌ No WhatsApp integrations found")
            return False
        
        print(f"✅ Found {len(integrations)} WhatsApp integration(s)")
        
        # Step 2: Process each integration
        for idx, integration in enumerate(integrations, 1):
            print(f"\n{'=' * 70}")
            print(f"Processing Integration {idx}/{len(integrations)}")
            print(f"{'=' * 70}")
            print(f"  ID: {integration.id}")
            print(f"  Project ID: {integration.project_id}")
            print(f"  Status: {integration.status}")
            
            session_id = integration.extra_data.get("session_id") if integration.extra_data else None
            print(f"  Session ID: {session_id}")
            
            if not session_id:
                print("  ⚠️  No session_id found - skipping")
                continue
            
            # Step 3: Delete session from WA-Gateway
            print(f"\n  🗑️  Deleting session from WA-Gateway...")
            try:
                if not settings.WA_GATEWAY_BASE_URL or not settings.WA_GATEWAY_API_KEY:
                    print("  ⚠️  WA_GATEWAY_BASE_URL or WA_GATEWAY_API_KEY not configured")
                    print("  ℹ️  You'll need to manually delete the session from WA-Gateway")
                else:
                    gateway = WhatsAppGatewayService(
                        base_url=settings.WA_GATEWAY_BASE_URL,
                        api_key=settings.WA_GATEWAY_API_KEY
                    )
                    
                    # Try to delete the session
                    try:
                        await gateway.delete_session(session_id)
                        print(f"  ✅ Session '{session_id}' deleted from WA-Gateway")
                    except Exception as e:
                        print(f"  ⚠️  Could not delete session: {e}")
                        print(f"  ℹ️  The session might already be deleted or WA-Gateway is unreachable")
            except Exception as e:
                print(f"  ⚠️  Error connecting to WA-Gateway: {e}")
            
            # Step 4: Update integration status in database
            print(f"\n  📝 Updating integration status...")
            integration.status = IntegrationStatus.PENDING
            if not integration.extra_data:
                integration.extra_data = {}
            integration.extra_data["needs_reset"] = True
            integration.extra_data["reset_reason"] = "encryption_error"
            integration.extra_data["reset_at"] = str(asyncio.get_event_loop().time())
            
            db.add(integration)
            await db.commit()
            print(f"  ✅ Integration marked for reset")
            
            # Step 5: Create new session
            print(f"\n  🆕 Creating new session...")
            try:
                if settings.WA_GATEWAY_BASE_URL and settings.WA_GATEWAY_API_KEY:
                    gateway = WhatsAppGatewayService(
                        base_url=settings.WA_GATEWAY_BASE_URL,
                        api_key=settings.WA_GATEWAY_API_KEY
                    )
                    
                    # Start new session
                    result = await gateway.start_session(session_id)
                    print(f"  ✅ New session created")
                    
                    # Get QR code
                    print(f"\n  📱 Fetching QR code...")
                    qr_result = await gateway.get_qr_code(session_id)
                    
                    if qr_result.get("qr"):
                        print(f"\n  {'=' * 70}")
                        print(f"  🔲 QR CODE FOR SESSION '{session_id}'")
                        print(f"  {'=' * 70}")
                        print(f"\n  QR Code URL: {qr_result.get('qr')}")
                        print(f"\n  📱 SCAN THIS QR CODE WITH YOUR PHONE:")
                        print(f"     1. Open WhatsApp on your phone")
                        print(f"     2. Go to Settings → Linked Devices")
                        print(f"     3. Tap 'Link a Device'")
                        print(f"     4. Scan the QR code from the URL above")
                        print(f"\n  ⏰ QR code expires in 60 seconds!")
                        print(f"  {'=' * 70}")
                    else:
                        print(f"  ⚠️  Could not fetch QR code")
                        print(f"  ℹ️  Please get QR code manually from your frontend")
                else:
                    print(f"  ⚠️  WA-Gateway not configured")
                    print(f"  ℹ️  Please reconnect from your frontend")
            except Exception as e:
                print(f"  ⚠️  Error creating new session: {e}")
                print(f"  ℹ️  Please reconnect from your frontend")
        
        # Final summary
        print(f"\n{'=' * 70}")
        print("✅ RESET COMPLETE")
        print("=" * 70)
        print("\n📋 Next Steps:")
        print("  1. Scan the QR code(s) shown above with your phone")
        print("  2. OR go to your frontend and reconnect WhatsApp")
        print("  3. Wait for 'Connected' status")
        print("  4. Send a test message to verify it's working")
        print("\n💡 Tips:")
        print("  - Make sure your phone has internet connection")
        print("  - Don't use the same number on multiple instances")
        print("  - If QR code expired, run this script again")
        print("=" * 70)
        
        return True

if __name__ == "__main__":
    try:
        result = asyncio.run(reset_whatsapp_session())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Aborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
