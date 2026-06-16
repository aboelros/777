import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.db.models import User, UserRole
from app.core.security import get_password_hash

async def create_arnold_admin():
    print("Creating admin user arnold@gmail.com...")
    async with AsyncSessionLocal() as session:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == "arnold@gmail.com")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("User already exists! Updating password and role...")
            existing.password_hash = get_password_hash("n01012012")
            existing.role = UserRole.ADMIN
            existing.is_active = True
        else:
            print("Creating new user...")
            new_user = User(
                email="arnold@gmail.com",
                password_hash=get_password_hash("n01012012"),
                name="Arnold",
                role=UserRole.ADMIN,
                is_active=True
            )
            session.add(new_user)
            
        await session.commit()
        print("✅ Successfully created/updated admin account: arnold@gmail.com")

if __name__ == "__main__":
    asyncio.run(create_arnold_admin())
