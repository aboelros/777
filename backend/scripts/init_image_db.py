import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import sys

# Add the backend directory to sys.path to import settings
sys.path.append(os.path.join(os.getcwd(), "app"))

async def init_image_db():
    # Priority 1: Environment Variable
    # Priority 2: Hardcoded Fallback (Corrected for current Supabase)
    db_url = os.getenv("IMAGE_STORAGE_DATABASE_URL")
    if not db_url:
        db_url = "postgresql+asyncpg://postgres.mrwmqimafmpywckflpoi:ana_b7b_noranty@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
    
    display_url = db_url.split('@')[1] if '@' in db_url else db_url
    print(f"🚀 Initializing image database at: {display_url}")
    
    engine = create_async_engine(
        db_url,
        connect_args={"statement_cache_size": 0}
    )
    
    try:
        async with engine.begin() as conn:
            # Create table for binary image storage in public schema
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.product_images (
                    id SERIAL PRIMARY KEY,
                    key TEXT UNIQUE NOT NULL,
                    data BYTEA NOT NULL,
                    content_type TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_product_images_key ON public.product_images(key)
            """))
            print("✅ Table 'public.product_images' created or already exists.")
            
            # Verify its visibility
            res = await conn.execute(text("SELECT count(*) FROM public.product_images"))
            print(f"📊 Current record count in product_images: {res.scalar()}")
            
    except Exception as e:
        print(f"❌ Failed to initialize image database: {e}")
        raise e
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_image_db())
