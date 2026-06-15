import asyncio
import sys
import os
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.config import settings
from app.db.models import Project, User

async def list_projects():
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("\n=== USERS ===")
        result = await session.execute(select(User))
        users = result.scalars().all()
        for user in users:
            print(f"User: {user.email} (ID: {user.id})")

        print("\n=== PROJECTS ===")
        result = await session.execute(select(Project))
        projects = result.scalars().all()
        if not projects:
            print("No projects found in database!")
        for project in projects:
            print(f"Project: {project.name} (Code: {project.project_code})")
            print(f"  ID: {project.id}")
            print(f"  Owner ID: {project.owner_id}")
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(list_projects())
