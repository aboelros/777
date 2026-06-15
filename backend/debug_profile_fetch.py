
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, text
from app.db.models import CustomerProfile, Integration
from app.core.config import settings
from uuid import UUID

async def inspect_db():
    # Use DATABASE_URL from settings
    db_url = settings.DATABASE_URL
    print(f"Connecting to (masked): {db_url.split('@')[-1] if '@' in db_url else db_url}")
    
    engine = create_async_engine(
        db_url,
        connect_args={"statement_cache_size": 0}
    )
    
    async with engine.connect() as conn:
        print("\n--- Project Inspection ---")
        # Find the project mentioned in logs
        project_id = "eaf71fdf-ffa6-4ff2-9f6d-7869c4b91d0f"
        print(f"Target Project ID: {project_id}")
        
        print("\n--- Customers in this Project ---")
        query = text(f"SELECT id, customer_id, name, avatar_url, last_sync FROM customer_profiles WHERE project_id = '{project_id}'")
        result = await conn.execute(query)
        customers = result.fetchall()
        for c in customers:
            print(f"ID: {c.id} | CID: {c.customer_id} | Name: {c.name} | Sync: {c.last_sync} | Avatar: {c.avatar_url[:50] if c.avatar_url else 'None'}")

        print("\n--- Integrations in this Project ---")
        query = text(f"SELECT id, provider, status, config FROM integrations WHERE project_id = '{project_id}'")
        result = await conn.execute(query)
        integrations = result.fetchall()
        for i in integrations:
            # Mask access token
            conf = i.config or {}
            token = conf.get("access_token", "N/A")
            masked_token = token[:5] + "..." + token[-5:] if len(token) > 10 else "SHORT"
            print(f"ID: {i.id} | Provider: {i.provider} | Status: {i.status} | Token: {masked_token}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(inspect_db())
