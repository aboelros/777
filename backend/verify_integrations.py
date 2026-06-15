import sys
import logging
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_imports():
    logger.info("Verifying imports...")
    try:
        from app.workers.tasks.core import (
            sync_shopify_orders, 
            send_message_task, 
            process_inbound_message,
            generate_ai_response,
            verify_integration,
            process_message_queue,
            generate_daily_reports,
            train_model,
            cleanup_old_logs
        )
        logger.info("✅ Worker tasks imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import worker tasks: {e}")
        sys.exit(1)

    try:
        from app.services.integrations.shopify import ShopifyService
        from app.services.integrations.whatsapp import WhatsAppService
        from app.services.integrations.telegram import TelegramService
        from app.services.integrations.instagram import InstagramClient
        from app.services.integrations.facebook import FacebookClient
        from app.services.gemini_client import GeminiClient
        logger.info("✅ Service classes imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import services: {e}")
        sys.exit(1)

def verify_instantiation():
    logger.info("Verifying service instantiation...")
    try:
        from app.services.integrations.shopify import ShopifyService
        s = ShopifyService("url", "key", "secret")
        logger.info("✅ ShopifyService instantiated")
        
        from app.services.integrations.whatsapp import WhatsAppService
        w = WhatsAppService("biz_id", "token")
        logger.info("✅ WhatsAppService instantiated")
        
        from app.services.integrations.telegram import TelegramService
        t = TelegramService("token")
        logger.info("✅ TelegramService instantiated")
        
        from app.services.integrations.instagram import InstagramClient
        i = InstagramClient({"page_id": "p", "access_token": "t"})
        logger.info("✅ InstagramClient instantiated")
        
        from app.services.integrations.facebook import FacebookClient
        f = FacebookClient({"page_id": "p", "access_token": "t", "app_secret": "s"})
        logger.info("✅ FacebookClient instantiated")
        
        from app.services.gemini_client import GeminiClient
        # Mock settings for Gemini
        from unittest.mock import patch
        with patch('app.core.config.settings.GEMINI_API_KEY', 'test_key'):
            g = GeminiClient()
            logger.info("✅ GeminiClient instantiated")
            
    except Exception as e:
        logger.error(f"❌ Failed to instantiate services: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Running Static Verification...")
    verify_imports()
    verify_instantiation()
    print("\n✅ All static checks passed! The code structure is valid.")
