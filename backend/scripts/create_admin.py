#!/usr/bin/env python
"""
Script to create an admin user.
Run with: python scripts/create_admin.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.db.models import User
from sqlalchemy import select


async def create_admin():
    """Create admin user interactively."""
    
    print("=" * 50)
    print("Create Admin User")
    print("=" * 50)
    
    # Get input
    email = input("Admin Email: ").strip()
    password = input("Admin Password (min 8 chars): ").strip()
    name = input("Admin Name: ").strip() or "Admin"
    
    if len(password) < 8:
        print("❌ Password must be at least 8 characters")
        return
    
    async with AsyncSessionLocal() as db:
        # Check if user exists
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"❌ User with email {email} already exists")
            return
        
        # Create admin user
        admin_user = User(
            email=email,
            password_hash=get_password_hash(password),
            name=name,
            role="admin",
            is_active=True
        )
        
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        
        print("\n✅ Admin user created successfully!")
        print(f"Email: {admin_user.email}")
        print(f"ID: {admin_user.id}")
        print(f"Role: {admin_user.role}")


if __name__ == "__main__":
    asyncio.run(create_admin())
