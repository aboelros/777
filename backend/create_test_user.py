"""
Script to manually create test user in the Auth Database.
Run this if the automatic seeding doesn't work.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

# Import models and utilities
import sys
sys.path.insert(0, '.')

from app.db.models import User, UserRole
from app.core.security import get_password_hash
from app.core.config import settings
from app.core.database import AuthBase


async def create_test_user():
    """Create test user in Auth Database."""
    
    print("=" * 60)
    print("Creating Test User in Auth Database")
    print("=" * 60)
    
    # Create engine for auth database
    engine = create_async_engine(settings.AUTH_DATABASE_URL)
    
    # Create tables
    print("\n📋 Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(AuthBase.metadata.create_all)
    print("✅ Tables created!")
    
    # Create session
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with SessionLocal() as db:
        # Check if user exists
        print("\n🔍 Checking if test user exists...")
        result = await db.execute(
            select(User).where(User.email == "test@aisales.local")
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("✅ Test user already exists!")
            print(f"   Email: {existing_user.email}")
            print(f"   ID: {existing_user.id}")
            print(f"   Role: {existing_user.role}")
        else:
            # Create test user
            print("\n👤 Creating test user...")
            test_user = User(
                email="test@aisales.local",
                password_hash=get_password_hash("AiSales2024!Demo"),
                name="Test User",
                role=UserRole.ADMIN,
                is_active=True
            )
            
            db.add(test_user)
            await db.commit()
            await db.refresh(test_user)
            
            print("✅ Test user created successfully!")
            print(f"   Email: {test_user.email}")
            print(f"   ID: {test_user.id}")
            print(f"   Role: {test_user.role}")
    
    await engine.dispose()
    
    print("\n" + "=" * 60)
    print("LOGIN CREDENTIALS")
    print("=" * 60)
    print("📧 Email:    test@aisales.local")
    print("🔑 Password: AiSales2024!Demo")
    print("=" * 60)
    print("\n✅ You can now login to your application!")


if __name__ == "__main__":
    asyncio.run(create_test_user())
