"""
Diagnostic script to check project ownership and help debug the 404 error.
"""

import asyncio
import sys
from pathlib import Path
from uuid import UUID

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

async def diagnose_project_access():
    """Diagnose project access issues."""
    from app.core.database import AsyncSessionLocal
    from app.db.models import User, Project
    from sqlalchemy import select
    
    print("=" * 70)
    print("🔍 Project Access Diagnostic Tool")
    print("=" * 70)
    
    # The project ID from the error
    problem_project_id = "5cf55643-2f3c-490c-9b45-a73f37cd14c2"
    
    async with AsyncSessionLocal() as db:
        # Find the project
        print(f"\n📋 Looking for project: {problem_project_id}")
        print("=" * 70)
        
        result = await db.execute(
            select(Project).where(Project.id == UUID(problem_project_id))
        )
        project = result.scalar_one_or_none()
        
        if not project:
            print(f"❌ Project NOT FOUND in database!")
            print(f"\n💡 This project ID doesn't exist. Possible causes:")
            print(f"   1. Project was deleted")
            print(f"   2. Wrong project ID in frontend")
            print(f"   3. Database was reset")
            
            # List all projects
            print(f"\n📋 All projects in database:")
            print("=" * 70)
            result = await db.execute(select(Project))
            all_projects = result.scalars().all()
            
            if not all_projects:
                print("❌ NO PROJECTS FOUND in database!")
                print("\n💡 Solution: Create a new project first")
            else:
                for p in all_projects:
                    print(f"\nProject: {p.name}")
                    print(f"  ID: {p.id}")
                    print(f"  Owner ID: {p.owner_id}")
                    print(f"  Created: {p.created_at}")
            
            return False
        
        print(f"✅ Project FOUND!")
        print(f"   Name: {project.name}")
        print(f"   Owner ID: {project.owner_id}")
        print(f"   Created: {project.created_at}")
        
        # Find the owner
        print(f"\n👤 Looking for project owner...")
        print("=" * 70)
        
        result = await db.execute(
            select(User).where(User.id == project.owner_id)
        )
        owner = result.scalar_one_or_none()
        
        if owner:
            print(f"✅ Owner FOUND!")
            print(f"   Name: {owner.name}")
            print(f"   Email: {owner.email}")
            print(f"   ID: {owner.id}")
        else:
            print(f"❌ Owner NOT FOUND!")
            print(f"   This is a database integrity issue!")
        
        # List all users
        print(f"\n👥 All users in database:")
        print("=" * 70)
        
        result = await db.execute(select(User))
        all_users = result.scalars().all()
        
        for user in all_users:
            print(f"\nUser: {user.name}")
            print(f"  Email: {user.email}")
            print(f"  ID: {user.id}")
            
            # Count their projects
            result = await db.execute(
                select(Project).where(Project.owner_id == user.id)
            )
            user_projects = result.scalars().all()
            print(f"  Projects: {len(user_projects)}")
            
            for p in user_projects:
                print(f"    - {p.name} (ID: {p.id})")
        
        # Solution
        print(f"\n" + "=" * 70)
        print("💡 SOLUTION")
        print("=" * 70)
        
        if owner:
            print(f"\n✅ The project exists and has a valid owner.")
            print(f"\n🔑 To access this project, you must:")
            print(f"   1. Log in as: {owner.email}")
            print(f"   2. Use the JWT token from that login")
            print(f"   3. Then you can access project: {project_id}")
            print(f"\n⚠️  If you're logged in as a DIFFERENT user, you'll get 404!")
        else:
            print(f"\n❌ The project exists but has no owner (database issue).")
            print(f"\n🔧 To fix:")
            print(f"   1. Delete this orphaned project")
            print(f"   2. Create a new project with a valid owner")
        
        return True

if __name__ == "__main__":
    try:
        asyncio.run(diagnose_project_access())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
