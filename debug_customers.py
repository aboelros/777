
import asyncio
from uuid import UUID
from sqlalchemy import select
from app.db.models import CustomerProfile, Message
from app.core.database import AsyncSessionLocal

async def debug_customers():
    async with AsyncSessionLocal() as db:
        # Search for customers mentioned in the screenshot/logs
        # tiger.5922118 (Instagram)
        # محمد بيه (Facebook)
        
        print("--- CUSTOMER DIAGNOSTIC ---")
        
        result = await db.execute(select(CustomerProfile))
        customers = result.scalars().all()
        
        for c in customers:
            print(f"ID: {c.id}")
            print(f"Name: {c.name}")
            print(f"Email: {c.email}")
            print(f"Phone: {c.phone}")
            print(f"Avatar: {c.avatar_url}")
            print(f"Platform ID: {c.platform_id}")
            print("-" * 20)

if __name__ == "__main__":
    asyncio.run(debug_customers())
