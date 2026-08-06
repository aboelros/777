import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load env variables
load_dotenv(Path(__file__).parent.parent / '.env')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.db.models import Project

from sqlalchemy import text

async def cleanup_duplicates():
    print("Cleaning up duplicate projects...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Project).order_by(Project.created_at.asc()))
        projects = result.scalars().all()
        
        seen_names = set()
        deleted_count = 0
        
        for project in projects:
            if project.name in seen_names:
                print(f"Deleting duplicate project: {project.name} (ID: {project.id})")
                await session.execute(text("DELETE FROM projects WHERE id = :id"), {"id": project.id})
                deleted_count += 1
            else:
                seen_names.add(project.name)
                print(f"Keeping project: {project.name} (ID: {project.id})")
                
        await session.commit()
        print(f"✅ Successfully deleted {deleted_count} duplicate projects.")

if __name__ == "__main__":
    asyncio.run(cleanup_duplicates())
