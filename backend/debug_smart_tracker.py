
import asyncio
import sys
import os
from datetime import datetime, timedelta
import structlog

# Add project root to path
sys.path.insert(0, '.')

from app.core.database import AsyncSessionLocal
from app.db.models import Order, Project
from sqlalchemy import select

async def debug_query():
    print("🚀 Starting Debug Query...")
    async with AsyncSessionLocal() as db:
        try:
            print("1. Fetching a project...")
            result = await db.execute(select(Project).limit(1))
            project = result.scalar_one_or_none()
            
            if not project:
                print("⚠️ No projects found. Creating dummy project for test...")
                # We can't really test the query without a project_id usually, 
                # but we can try running the query with a random UUID if needed,
                # or just skip. For reproduction, we need a valid query.
                return

            print(f"✅ Found project: {project.id}")
            
            trigger_status = "delivered"
            delay_hours = 24
            cutoff_time = datetime.utcnow() - timedelta(hours=delay_hours)
            window_start = cutoff_time - timedelta(hours=24)
            
            print(f"2. Building Query for status='{trigger_status}'...")
            stmt = select(Order).where(
                Order.project_id == project.id,
                Order.status == trigger_status,
                Order.last_updated <= cutoff_time,
                Order.last_updated >= window_start
            )
            
            print(f"3. Executing Query...")
            # This is where it should fail if column is wrong
            result = await db.execute(stmt)
            orders = result.scalars().all()
            
            print(f"✅ Query Successful! Found {len(orders)} orders.")
            
        except Exception as e:
            print("\n❌ CRITICAL ERROR CAUGHT:")
            print(f"Type: {type(e)}")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Ensure Windows compatibility for asyncio loop policy if needed
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(debug_query())
