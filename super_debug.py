
import asyncio
from sqlalchemy import select, text
from app.db.models import Integration, CustomerProfile, Message
from app.core.database import AsyncSessionLocal
import structlog

async def super_debug():
    async with AsyncSessionLocal() as db:
        print("\n--- 🕵️ SUPER DEBUG: MESSAGES & PROFILES ---")
        
        # 1. Check Integrations
        print("\n[1] Checking Integrations...")
        int_res = await db.execute(select(Integration))
        integrations = int_res.scalars().all()
        print(f"Found {len(integrations)} integrations.")
        for i in integrations:
            print(f"  - ID: {i.id} | Provider: {i.provider} | Status: {i.status}")

        # 2. Check Customer Profiles
        print("\n[2] Checking Customer Profiles (Sample)...")
        cust_res = await db.execute(select(CustomerProfile).limit(10))
        customers = cust_res.scalars().all()
        for c in customers:
            print(f"  - ID: {c.id} | Name: {c.name} | Avatar: {c.avatar_url[:50] if c.avatar_url else 'None'}")

        # 3. Check for Orphans
        print("\n[3] Checking for Orphan Messages (no customer_id)...")
        orphan_res = await db.execute(select(Message).where(Message.customer_id == None).limit(5))
        orphans = orphan_res.scalars().all()
        print(f"Sample orphans: {len(orphans)}")
        for o in orphans:
             print(f"  - Msg ID: {o.id} | Platform: {o.platform} | Sender: {o.sender}")

        # 4. Check Storage Table (if using Postgres storage)
        print("\n[4] Checking Image Storage Table...")
        try:
            storage_res = await db.execute(text("SELECT key, content_type, size FROM public.product_images LIMIT 5"))
            rows = storage_res.fetchall()
            print(f"Found {len(rows)} images in storage table.")
            for r in rows:
                print(f"  - Key: {r[0]} | Type: {r[1]} | Size: {r[2]}")
        except Exception as e:
            print(f"  - Storage table check failed (might not exist): {str(e)}")

        print("\n--- DEBUG COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(super_debug())
