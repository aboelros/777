
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, text
from app.db.models import CustomerProfile, Message
from app.core.config import settings

async def check_data():
    # Use the DB URL from the environment
    db_url = "postgresql+asyncpg://postgres:10052008mariem@vjdbthhdyemeugyhucoq.pooler.supabase.com:5432/postgres"
    print(f"Connecting to: {db_url.split('@')[-1]}")
    
    engine = create_async_engine(db_url)
    try:
        async with engine.connect() as conn:
            # Check customers
            result = await conn.execute(text("SELECT id, name, avatar_url FROM customer_profiles LIMIT 10"))
            customers = result.fetchall()
            print("\n--- Customers ---")
            for c in customers:
                print(f"ID: {c.id} | Name: {c.name} | Avatar: {c.avatar_url[:50] if c.avatar_url else 'None'}...")

            # Check messages
            result = await conn.execute(text("SELECT id, content, platform, direction FROM messages ORDER BY created_at DESC LIMIT 10"))
            messages = result.fetchall()
            print("\n--- Last 10 Messages ---")
            for m in messages:
                print(f"ID: {m.id} | Dir: {m.direction} | Platform: {m.platform} | Content: {str(m.content)[:50]}...")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_data())
