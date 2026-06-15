"""
Script to check database connection and verify test user exists.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, text
import time

import sys
sys.path.insert(0, '.')

from app.db.models import User, Project
from app.core.config import settings


async def check_database():
    """Check Database connection and data."""
    print("\n" + "=" * 60)
    print("🔐 CHECKING DATABASE")
    print("=" * 60)
    
    try:
        # Create engine
        db_url = settings.DATABASE_URL.replace("localhost", "127.0.0.1")
        if not db_url:
             db_url = "postgresql+asyncpg://aisales:changeme@127.0.0.1:5432/aisales"
        
        print(f"🔌 Connecting to: {db_url.split('@')[-1]}")
        engine = create_async_engine(db_url, echo=False)
        
        # Test connection
        print("\n🔌 Testing connection...")
        start_time = time.time()
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
        connection_time = time.time() - start_time
        print(f"✅ Connection successful! ({connection_time:.2f}s)")
        
        # Check users and projects tables
        SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with SessionLocal() as db:
            # Count users
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            print(f"\n👥 Users in database: {len(users)}")
            for user in users:
                print(f"   - {user.email} (ID: {user.id}, Role: {user.role})")
            
            # Count projects
            result = await db.execute(select(Project))
            projects = result.scalars().all()
            
            print(f"\n📁 Projects in database: {len(projects)}")
            for project in projects:
                print(f"   - {project.name} (ID: {project.id})")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def main():
    """Run all checks."""
    print("\n" + "🔍" * 30)
    print("DATABASE CONNECTION CHECK")
    print("🔍" * 30)
    
    db_ok = await check_database()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Database: {'✅ OK' if db_ok else '❌ FAILED'}")
    print("=" * 60)
    
    if not db_ok:
        print("\n⚠️  Database has issues!")
        print("Check your connection settings or run migrations.")


if __name__ == "__main__":
    asyncio.run(main())
