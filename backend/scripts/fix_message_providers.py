import asyncio
import sys
import os
import sqlalchemy
from sqlalchemy import select, update, or_, and_
from uuid import UUID

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

# Try loading .env from multiple possible locations
env_paths = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')),
    os.path.abspath(os.path.join(os.getcwd(), 'backend', '.env')),
    os.path.abspath(os.path.join(os.getcwd(), '.env'))
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded env from: {env_path}")
        break

# Handle Database URL construction
db_url = os.getenv("APP_DATABASE_URL") or os.getenv("DATABASE_URL")
if not db_url:
    print("CRITICAL: Neither APP_DATABASE_URL nor DATABASE_URL found in environment!")
    sys.exit(1)

# Ensure it's using the asyncpg driver
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

print(f"Found database configuration: {db_url.split('@')[-1] if '@' in db_url else 'configured'}")

from app.core.database import AsyncSessionLocal, engine
from app.db.models import Message

async def fix_message_providers():
    print("Starting message provider standardization...")
    
    async with AsyncSessionLocal() as db:
        # 1. Standardize Instagram messages
        print("Fixing Instagram messages...")
        stmt = (
            update(Message)
            .where(or_(Message.provider == "instagram", Message.platform == "instagram"))
            .values(provider="meta", platform="instagram")
        )
        result = await db.execute(stmt)
        print(f"Processed Instagram messages.")
        
        # 2. Standardize Facebook messages
        print("Fixing Facebook messages...")
        stmt = (
            update(Message)
            .where(or_(Message.provider == "facebook", Message.platform == "facebook"))
            .values(provider="meta", platform="facebook")
        )
        result = await db.execute(stmt)
        print(f"Processed Facebook messages.")
        
        # 3. Standardize WhatsApp messages
        print("Fixing WhatsApp messages...")
        stmt = (
            update(Message)
            .where(or_(Message.provider == "whatsapp", Message.platform == "whatsapp"))
            .values(provider="meta", platform="whatsapp")
        )
        result = await db.execute(stmt)
        print(f"Processed WhatsApp messages.")
        
        await db.commit()
        
        # 4. Link messages to customer profiles where missing
        print("Linking messages to customer profiles...")
        from app.db.models import CustomerProfile
        
        # Find all unlinked messages
        result = await db.execute(
            select(Message).where(Message.customer_id == None)
        )
        unlinked_messages = result.scalars().all()
        print(f"Found {len(unlinked_messages)} unlinked messages.")
        
        linked_count = 0
        for msg in unlinked_messages:
            customer_payload = (msg.sender if msg.direction == "inbound" else msg.recipient) or {}
            platform_id = customer_payload.get("id") or customer_payload.get("customer_id")
            
            if platform_id:
                # Find customer by platform ID
                cust_query = select(CustomerProfile).where(
                    CustomerProfile.project_id == msg.project_id,
                    or_(
                        CustomerProfile.customer_id == str(platform_id),
                        CustomerProfile.platform_accounts.contains({msg.platform: str(platform_id)})
                    )
                )
                cust_result = await db.execute(cust_query)
                customer = cust_result.scalar_one_or_none()
                
                if customer:
                    msg.customer_id = customer.id
                    linked_count += 1
        
        await db.commit()
        print(f"Successfully linked {linked_count} messages to profiles.")
        print("Standardization complete!")

if __name__ == "__main__":
    try:
        asyncio.run(fix_message_providers())
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
