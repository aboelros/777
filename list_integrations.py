import asyncio
import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath("backend"))

from app.core.database import AsyncSessionLocal
from app.db.models import Integration
from sqlalchemy import select
from uuid import UUID

async def list_integrations():
    project_id = UUID("197b738f-84b0-41c7-9dfc-d896b9b575f2")
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Integration).where(Integration.project_id == project_id)
        )
        integrations = result.scalars().all()
        
        print(f"Found {len(integrations)} integrations:")
        for i in integrations:
            print(f"ID: {i.id} | Provider: {i.provider} | Status: {i.status}")
            print(f"  Config: {i.config}")
            print(f"  Extra: {i.extra_data}")
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(list_integrations())
