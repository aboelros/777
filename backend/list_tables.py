
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def list_tables():
    url = settings.IMAGE_STORAGE_DATABASE_URL or settings.DATABASE_URL
    print(f"Connecting to: {url.split('@')[-1] if '@' in url else url}")
    
    engine = create_async_engine(url, connect_args={"statement_cache_size": 0})
    
    async with engine.connect() as conn:
        # Check connection
        res = await conn.execute(text("SELECT current_schema(), current_database()"))
        schema, db = res.fetchone()
        print(f"Connected to DB: {db}, Current Schema: {schema}")
        
        # List all tables in public schema
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = result.fetchall()
        print("\nTables in 'public' schema:")
        found = False
        for t in tables:
            print(f"- {t[0]}")
            if t[0] == 'product_images':
                found = True
        
        if found:
            print("\n✅ 'product_images' table FOUND!")
        else:
            print("\n❌ 'product_images' table NOT FOUND!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(list_tables())
