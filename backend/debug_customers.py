
import asyncio
from uuid import UUID
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.db.models import CustomerProfile, Integration, Message

async def debug_tiger():
    async with AsyncSessionLocal() as db:
        print("\n--- Searching for 'tiger' customer ---")
        result = await db.execute(
            select(CustomerProfile).where(CustomerProfile.name.ilike("%tiger%"))
        )
        customers = result.scalars().all()
        if not customers:
            print("No 'tiger' customer found by name. Searching by recent messages...")
            result = await db.execute(
                select(Message).order_by(Message.created_at.desc()).limit(10)
            )
            msgs = result.scalars().all()
            for m in msgs:
                print(f"Msg: {m.content[:20]} from {m.customer_id}")
            return

        for c in customers:
            print(f"ID: {c.id}")
            print(f"Name: {c.name}")
            print(f"CID: {c.customer_id}")
            print(f"Avatar: {c.avatar_url}")
            print(f"Last Sync: {c.last_sync}")
            print(f"Platform Accounts: {c.platform_accounts}")
            print("-" * 20)
            
            # Check messages for this customer
            result = await db.execute(
                select(Message).where(Message.customer_id == c.id).order_by(Message.created_at.desc()).limit(1)
            )
            last_msg = result.scalar_one_or_none()
            if last_msg:
                print(f"Last Msg Platform: {last_msg.platform}, Provider: {last_msg.provider}")
                print(f"Last Msg Content: {last_msg.content[:50]}")

        # Check integrations specifically for this project
        if customers:
            project_id = customers[0].project_id
            print(f"\n--- Integrations for Project: {project_id} ---")
            result = await db.execute(
                select(Integration).where(Integration.project_id == project_id)
            )
            integrations = result.scalars().all()
            for i in integrations:
                print(f"ID: {i.id}, Provider: {i.provider}, Status: {i.status}")

if __name__ == "__main__":
    asyncio.run(debug_tiger())
