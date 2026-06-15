import asyncio
import sys
import os
from sqlalchemy import select
from datetime import datetime, timedelta

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.core.database import AsyncSessionLocal
from app.db.models import Message

async def check_queued_messages():
    print("Checking for queued messages in the last hour...")
    cutoff = datetime.utcnow() - timedelta(hours=1)
    
    async with AsyncSessionLocal() as db:
        stmt = (
            select(Message)
            .where(Message.created_at >= cutoff)
            .where(Message.direction == "outbound")
            .order_by(Message.created_at.desc())
        )
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        # Check integrations
        print("\nChecking integration status...")
        from app.db.models import Integration
        int_stmt = select(Integration)
        int_res = await db.execute(int_stmt)
        integrations = int_res.scalars().all()
        for i in integrations:
             print(f"Provider: {i.provider} | Status: {i.status} | Project: {i.project_id}")

if __name__ == "__main__":
    asyncio.run(check_queued_messages())
