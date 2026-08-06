
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def verify_settings():
    print("\n--- Settings Verification ---")
    print(f"ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"DATABASE_URL (masked): {settings.DATABASE_URL.split('@')[-1]}")
    
    storage_url = settings.IMAGE_STORAGE_DATABASE_URL
    if storage_url:
        print(f"IMAGE_STORAGE_DATABASE_URL (masked): {storage_url.split('@')[-1]}")
        
        # Test connection
        print("\n--- Testing Storage DB Connection ---")
        try:
            # We need to make sure the URL is in the right format (postgresql+asyncpg://)
            # The validator in config.py should have handled this, but let's be sure.
            engine = create_async_engine(
                storage_url,
                connect_args={"statement_cache_size": 0}
            )
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                print(f"✅ Connection successful: {result.fetchone()}")
                
                # Check if table exists
                result = await conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'product_images')"))
                print(f"📊 Table 'product_images' exists: {result.scalar()}")
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
    else:
        print("⚠️ IMAGE_STORAGE_DATABASE_URL is not set!")

if __name__ == "__main__":
    asyncio.run(verify_settings())
