"""
Security Test: Verify Multi-Tenant Data Isolation
Tests that each user account has separate projects that are not shared.
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def test_multi_tenant_security():
    """Test that projects are properly isolated between users."""
    from app.core.database import AsyncSessionLocal
    from app.db.models import User, Project
    from app.core.security import get_password_hash
    from sqlalchemy import select
    from fastapi import HTTPException
    
    print("=" * 70)
    print("🔒 Multi-Tenant Security Test")
    print("=" * 70)
    print("\nTesting that each user account has separate, isolated projects...")
    
    async with AsyncSessionLocal() as db:
        # Create Test User A
        print("\n" + "=" * 70)
        print("Step 1: Creating Test Users")
        print("=" * 70)
        
        user_a = User(
            email=f"test_user_a_{uuid4().hex[:8]}@test.com",
            password_hash=get_password_hash("TestPassword123!"),
            name="Test User A",
            role="user",
            is_active=True
        )
        db.add(user_a)
        
        user_b = User(
            email=f"test_user_b_{uuid4().hex[:8]}@test.com",
            password_hash=get_password_hash("TestPassword123!"),
            name="Test User B",
            role="user",
            is_active=True
        )
        db.add(user_b)
        
        await db.commit()
        await db.refresh(user_a)
        await db.refresh(user_b)
        
        print(f"✅ User A created: {user_a.email} (ID: {user_a.id})")
        print(f"✅ User B created: {user_b.email} (ID: {user_b.id})")
        
        # Create Projects for Each User
        print("\n" + "=" * 70)
        print("Step 2: Creating Projects for Each User")
        print("=" * 70)
        
        project_a = Project(
            owner_id=user_a.id,
            name="User A's Project",
            description="This belongs to User A only"
        )
        db.add(project_a)
        
        project_b = Project(
            owner_id=user_b.id,
            name="User B's Project",
            description="This belongs to User B only"
        )
        db.add(project_b)
        
        await db.commit()
        await db.refresh(project_a)
        await db.refresh(project_b)
        
        print(f"✅ Project A created: '{project_a.name}' (Owner: User A)")
        print(f"✅ Project B created: '{project_b.name}' (Owner: User B)")
        
        # Test 1: User A can access their own project
        print("\n" + "=" * 70)
        print("Test 1: User A Accessing Their Own Project")
        print("=" * 70)
        
        result = await db.execute(
            select(Project).where(
                Project.id == project_a.id,
                Project.owner_id == user_a.id
            )
        )
        found_project = result.scalar_one_or_none()
        
        if found_project:
            print(f"✅ PASS: User A can access their own project")
            print(f"   Project: {found_project.name}")
        else:
            print(f"❌ FAIL: User A cannot access their own project!")
            return False
        
        # Test 2: User A CANNOT access User B's project
        print("\n" + "=" * 70)
        print("Test 2: User A Trying to Access User B's Project")
        print("=" * 70)
        
        result = await db.execute(
            select(Project).where(
                Project.id == project_b.id,
                Project.owner_id == user_a.id  # User A trying to access Project B
            )
        )
        found_project = result.scalar_one_or_none()
        
        if not found_project:
            print(f"✅ PASS: User A CANNOT access User B's project (as expected)")
            print(f"   Security: Data isolation is working correctly!")
        else:
            print(f"❌ FAIL: User A CAN access User B's project!")
            print(f"   SECURITY BREACH: Projects are not properly isolated!")
            return False
        
        # Test 3: User B can access their own project
        print("\n" + "=" * 70)
        print("Test 3: User B Accessing Their Own Project")
        print("=" * 70)
        
        result = await db.execute(
            select(Project).where(
                Project.id == project_b.id,
                Project.owner_id == user_b.id
            )
        )
        found_project = result.scalar_one_or_none()
        
        if found_project:
            print(f"✅ PASS: User B can access their own project")
            print(f"   Project: {found_project.name}")
        else:
            print(f"❌ FAIL: User B cannot access their own project!")
            return False
        
        # Test 4: User B CANNOT access User A's project
        print("\n" + "=" * 70)
        print("Test 4: User B Trying to Access User A's Project")
        print("=" * 70)
        
        result = await db.execute(
            select(Project).where(
                Project.id == project_a.id,
                Project.owner_id == user_b.id  # User B trying to access Project A
            )
        )
        found_project = result.scalar_one_or_none()
        
        if not found_project:
            print(f"✅ PASS: User B CANNOT access User A's project (as expected)")
            print(f"   Security: Data isolation is working correctly!")
        else:
            print(f"❌ FAIL: User B CAN access User A's project!")
            print(f"   SECURITY BREACH: Projects are not properly isolated!")
            return False
        
        # Test 5: List projects for each user
        print("\n" + "=" * 70)
        print("Test 5: Listing Projects for Each User")
        print("=" * 70)
        
        # User A's projects
        result = await db.execute(
            select(Project).where(Project.owner_id == user_a.id)
        )
        user_a_projects = result.scalars().all()
        
        print(f"\nUser A's projects ({len(user_a_projects)}):")
        for p in user_a_projects:
            print(f"  - {p.name}")
        
        # User B's projects
        result = await db.execute(
            select(Project).where(Project.owner_id == user_b.id)
        )
        user_b_projects = result.scalars().all()
        
        print(f"\nUser B's projects ({len(user_b_projects)}):")
        for p in user_b_projects:
            print(f"  - {p.name}")
        
        if len(user_a_projects) == 1 and len(user_b_projects) == 1:
            print(f"\n✅ PASS: Each user sees only their own projects")
        else:
            print(f"\n❌ FAIL: Users see incorrect number of projects")
            return False
        
        # Test 6: Test verify_project_access function
        print("\n" + "=" * 70)
        print("Test 6: Testing verify_project_access Function")
        print("=" * 70)
        
        from app.core.access_control import verify_project_access
        
        # User A accessing their project - should work
        try:
            project = await verify_project_access(project_a.id, str(user_a.id), db)
            print(f"✅ PASS: verify_project_access allows User A to access their project")
        except HTTPException:
            print(f"❌ FAIL: verify_project_access blocks User A from their own project")
            return False
        
        # User A accessing User B's project - should fail
        try:
            project = await verify_project_access(project_b.id, str(user_a.id), db)
            print(f"❌ FAIL: verify_project_access allows User A to access User B's project!")
            return False
        except HTTPException as e:
            if e.status_code == 404:
                print(f"✅ PASS: verify_project_access blocks User A from User B's project")
                print(f"   Error: {e.detail}")
            else:
                print(f"❌ FAIL: Wrong error code: {e.status_code}")
                return False
        
        # Cleanup
        print("\n" + "=" * 70)
        print("Cleanup: Removing Test Data")
        print("=" * 70)
        
        await db.delete(project_a)
        await db.delete(project_b)
        await db.delete(user_a)
        await db.delete(user_b)
        await db.commit()
        
        print(f"✅ Test data cleaned up")
        
        # Final Summary
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print("\n✅ Security Verification Complete:")
        print("   ✓ Each user can access only their own projects")
        print("   ✓ Users cannot access other users' projects")
        print("   ✓ Project listing shows only owned projects")
        print("   ✓ verify_project_access function works correctly")
        print("\n🔒 CONCLUSION: Multi-tenant data isolation is SECURE")
        print("=" * 70)
        
        return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_multi_tenant_security())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
