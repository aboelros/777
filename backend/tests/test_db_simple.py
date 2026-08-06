#!/usr/bin/env python3
"""
Simple database test script.
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_db():
    """Test database connection."""
    try:
        from app.core.config import settings
        from app.core.database import AsyncSessionLocal, engine
        from app.db.models import User, Project
        from sqlalchemy import select, text
        
        print(f"🔍 Testing database connection...")
        print(f"📍 Database URL: {settings.DATABASE_URL[:50]}...")
        print(f"🧪 Testing mode: {settings.TESTING_MODE}")
        
        # Test basic connection
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            test_result = result.scalar()
            print(f"✅ Basic connection test: {test_result}")
        
        # Test session and models
        async with AsyncSessionLocal() as db:
            # Count users
            result = await db.execute(select(User))
            users = result.scalars().all()
            print(f"👥 Users in database: {len(users)}")
            
            # Count projects  
            result = await db.execute(select(Project))
            projects = result.scalars().all()
            print(f"📁 Projects in database: {len(projects)}")
            
            # If no users, create test user
            if len(users) == 0:
                print("🔧 Creating test user...")
                from app.core.security import get_password_hash
                from uuid import uuid4
                
                test_user = User(
                    id=uuid4(),
                    email="test@aisales.local",
                    password_hash=get_password_hash("AiSales2024!Demo"),
                    name="Test User",
                    role="admin",
                    is_active=True
                )
                
                db.add(test_user)
                await db.commit()
                print("✅ Test user created!")
                
                # Create test project
                test_project = Project(
                    owner_id=test_user.id,
                    name="Test Project",
                    description="Test project for development",
                    timezone="UTC"
                )
                
                db.add(test_project)
                await db.commit()
                print("✅ Test project created!")
        
        print("🎉 Database test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_db())
    sys.exit(0 if success else 1)
