"""
Database seeding - Creates a simple test account for localhost testing.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.db.models import User, UserRole, Project
from app.core.security import get_password_hash

logger = structlog.get_logger(__name__)


async def create_test_account(db: AsyncSession) -> User:
    """
    Create test account with secure credentials for localhost testing.
    
    Credentials:
    - Email: test@aisales.local
    - Password: AiSales2024!Demo
    
    Returns:
        User: Created or existing test user
    """
    # Check if test user exists
    result = await db.execute(
        select(User).where(User.email == "test@aisales.local")
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        logger.info("✅ Test user already exists", email="test@aisales.local")
        return existing_user
    
    # Create test user with admin role
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
    
    logger.info(
        "✅ Test account created successfully!",
        email="test@aisales.local",
        password="AiSales2024!Demo",
        user_id=str(test_user.id)
    )
    
    return test_user


async def create_demo_project(db: AsyncSession, user: User) -> Project:
    """Create a demo project for the test user."""
    # Check if project exists
    result = await db.execute(
        select(Project).where(
            Project.owner_id == user.id,
            Project.name == "Test Project"
        )
    )
    existing_project = result.scalar_one_or_none()
    
    if existing_project:
        logger.info("✅ Demo project already exists")
        return existing_project
    
    # Create demo project
    demo_project = Project(
        owner_id=user.id,
        name="Test Project",
        project_code="TEST-PROJECT-001",
        description="Test project for localhost development",
        timezone="UTC",
        settings={
            "ai_enabled": True,
            "auto_response": True,
            "language": "en"
        },
        is_active=True
    )
    
    db.add(demo_project)
    await db.commit()
    await db.refresh(demo_project)
    
    logger.info("✅ Demo project created", project_name=demo_project.name)
    
    return demo_project


async def seed_database(db: AsyncSession):
    """
    Seed database with test account for localhost.
    
    Creates:
    - Test user: test@aisales.local / AiSales2024!Demo
    - Demo project for testing
    """
    logger.info("🌱 Seeding database with test account...")
    
    try:
        # Create test user
        test_user = await create_test_account(db)
        
        # Create demo project
        await create_demo_project(db, test_user)
        
        logger.info("=" * 60)
        logger.info("✅ DATABASE READY FOR TESTING!")
        logger.info("=" * 60)
        logger.info("📧 Email: test@aisales.local")
        logger.info("🔑 Password: AiSales2024!Demo")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error("❌ Database seeding failed", error=str(e), exc_info=True)
        raise
