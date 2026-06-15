"""
Refresh Customer Identities Script.
Iterates through customers with generic names and fetches real names from Meta API.
"""
import asyncio
import os
import sys
from uuid import UUID

# Add backend to path and load env
backend_dir = os.path.join(os.getcwd(), 'backend')
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

# Force DATABASE_URL for settings
import os
os.environ["DATABASE_URL"] = os.getenv("APP_DATABASE_URL") or ""

from app.core.database import AsyncSessionLocal
from app.db.models import CustomerProfile, Integration, IntegrationStatus
from app.services.integrations.facebook import FacebookClient
from sqlalchemy import select

async def refresh_identities():
    from app.core.config import settings
    print(f"🚀 Starting Customer Identity Refresh using DB: {settings.DATABASE_URL.split('@')[-1] if settings.DATABASE_URL else 'None'}")
    
    async with AsyncSessionLocal() as db:
        # 1. Find customers with generic names
        generic_names = ["Unknown", "Instagram User", "Facebook User", "Facebook Profile"]
        query = select(CustomerProfile).where(
            (CustomerProfile.name.in_(generic_names)) | (CustomerProfile.name == None)
        )
        result = await db.execute(query)
        customers = result.scalars().all()
        
        print(f"🔍 Found {len(customers)} customers with generic names.")
        
        if not customers:
            print("✅ All customers have unique names. Nothing to do.")
            return

        # 2. Iterate and fetch
        updated_count = 0
        for customer in customers:
            # Determine platform (infer from platform_accounts)
            platform = None
            if customer.platform_accounts:
                if "instagram" in customer.platform_accounts:
                    platform = "instagram"
                elif "facebook" in customer.platform_accounts:
                    platform = "facebook"
            
            if not platform:
                continue
                
            sender_id = customer.platform_accounts.get(platform)
            if not sender_id:
                continue
                
            # Get integration for this project
            int_query = select(Integration).where(
                Integration.project_id == customer.project_id,
                Integration.provider == platform,
                Integration.status == IntegrationStatus.CONNECTED
            )
            int_result = await db.execute(int_query)
            integration = int_result.scalars().first()
            
            if not integration:
                print(f"⚠️ No connected {platform} integration found for project {customer.project_id}")
                continue
                
            try:
                client = FacebookClient(integration.config)
                profile = await client.get_user_profile(sender_id, platform=platform)
                
                real_name = None
                if platform == "instagram":
                    real_name = profile.get("username") or profile.get("name")
                else:
                    real_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
                
                if real_name and real_name not in generic_names:
                    print(f"✅ Resolved: {customer.name} -> {real_name}")
                    customer.name = real_name
                    db.add(customer)
                    updated_count += 1
                else:
                    print(f"ℹ️ Could not resolve real name for {customer.customer_id}")
                    
            except Exception as e:
                print(f"❌ Error resolving {customer.customer_id}: {str(e)}")

        if updated_count > 0:
            await db.commit()
            print(f"✨ Successfully updated {updated_count} customer identities.")
        else:
            print("🏁 No updates were made.")

if __name__ == "__main__":
    asyncio.run(refresh_identities())
