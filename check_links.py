
import asyncio
from sqlalchemy import select
from app.db.models import Message, CustomerProfile
from app.core.database import AsyncSessionLocal

async def check_message_links():
    async with AsyncSessionLocal() as db:
        print("--- MESSAGE-CUSTOMER LINK DIAGNOSTIC ---")
        
        # Check for orphan messages (no customer_id)
        result = await db.execute(
            select(Message).where(Message.customer_id == None).limit(50)
        )
        orphans = result.scalars().all()
        
        print(f"Found {len(orphans)} sample orphan messages (limit 50).")
        for m in orphans:
            print(f"Msg ID: {m.id} | Platform: {m.platform} | Sender JSON: {m.sender}")

        # Check for total counts
        total_msg_res = await db.execute(select(Message))
        total_msg = len(total_msg_res.scalars().all())
        
        linked_msg_res = await db.execute(select(Message).where(Message.customer_id != None))
        linked_msg = len(linked_msg_res.scalars().all())
        
        print(f"\nTotal Messages: {total_msg}")
        print(f"Linked Messages: {linked_msg}")
        print(f"Orphan Messages: {total_msg - linked_msg}")

if __name__ == "__main__":
    asyncio.run(check_message_links())
