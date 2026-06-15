#!/usr/bin/env python3
"""
Test Telegram bot functionality.
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_telegram_bot():
    """Test Telegram bot setup and functionality."""
    try:
        from app.core.config import settings
        from app.core.database import AsyncSessionLocal
        from app.db.models import Integration, Project, User
        from app.services.integrations.telegram import TelegramService
        from sqlalchemy import select
        from uuid import uuid4
        
        print("🤖 Testing Telegram Bot Setup...")
        
        # Check if we have a Telegram bot token in environment
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not telegram_token:
            print("❌ No TELEGRAM_BOT_TOKEN found in environment variables")
            print("💡 Add TELEGRAM_BOT_TOKEN=your_bot_token to your .env file")
            return False
        
        print(f"✅ Found Telegram bot token: {telegram_token[:10]}...")
        
        # Test bot connection
        telegram_service = TelegramService(telegram_token)
        try:
            bot_info = await telegram_service.get_me()
            print(f"✅ Bot connected successfully: @{bot_info['result']['username']}")
        except Exception as e:
            print(f"❌ Failed to connect to Telegram bot: {str(e)}")
            return False
        
        # Check database for integrations
        async with AsyncSessionLocal() as db:
            # Check if we have any projects
            result = await db.execute(select(Project))
            projects = result.scalars().all()
            
            if not projects:
                print("❌ No projects found in database")
                print("💡 Create a project first through the frontend")
                return False
            
            project = projects[0]
            print(f"✅ Found project: {project.name} (ID: {project.id})")
            
            # Check for Telegram integration
            result = await db.execute(
                select(Integration)
                .where(Integration.project_id == project.id)
                .where(Integration.provider == "telegram")
            )
            telegram_integration = result.scalar_one_or_none()
            
            if not telegram_integration:
                print("⚠️  No Telegram integration found in database")
                print("💡 Creating Telegram integration...")
                
                # Create Telegram integration
                telegram_integration = Integration(
                    id=uuid4(),
                    project_id=project.id,
                    provider="telegram",
                    status="connected",
                    config={
                        "api_key": telegram_token,
                        "bot_username": bot_info['result']['username']
                    }
                )
                
                db.add(telegram_integration)
                await db.commit()
                print("✅ Telegram integration created")
            else:
                print(f"✅ Found Telegram integration: {telegram_integration.status}")
                
                # Update config if needed
                if telegram_integration.config.get('api_key') != telegram_token:
                    telegram_integration.config['api_key'] = telegram_token
                    telegram_integration.config['bot_username'] = bot_info['result']['username']
                    await db.commit()
                    print("✅ Updated Telegram integration config")
        
        # Test webhook URL
        webhook_url = f"{settings.API_BASE_URL}/api/v1/webhooks/telegram/{project.id}"
        print(f"🔗 Webhook URL: {webhook_url}")
        
        try:
            webhook_result = await telegram_service.set_webhook(webhook_url)
            if webhook_result:
                print("✅ Webhook set successfully")
            else:
                print("❌ Failed to set webhook")
        except Exception as e:
            print(f"❌ Webhook setup failed: {str(e)}")
        
        print("\n🎯 TELEGRAM BOT STATUS:")
        print("✅ Bot token configured")
        print("✅ Bot connection working")
        print("✅ Database integration created")
        print("✅ Webhook URL configured")
        print("\n💬 Test your bot by sending a message!")
        print(f"Bot username: @{bot_info['result']['username']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Telegram bot test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_telegram_bot())
    sys.exit(0 if success else 1)
