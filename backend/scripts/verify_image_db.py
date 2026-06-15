import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Test script for image storage
async def verify_image_db():
    db_url = "postgresql+asyncpg://postgres.mrwmqimafmpywckflpoi:ana_b7b_noranty@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
    engine = create_async_engine(db_url)
    
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT count(*) FROM product_images"))
            count = result.scalar()
            print(f"✅ Connection successful! Current image count: {count}")
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify_image_db())
