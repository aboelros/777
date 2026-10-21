"""
Seeding script for Meta App Review test accounts.
Creates 4 fully provisioned store accounts with active Meta integrations,
realistic products, customer profiles, orders, and conversation messages.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Setup path to import backend app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
import app.db.models  # Ensures all ORM models (ModelTraining, Report, etc.) are registered
from app.domains.auth.models import User, UserRole
from app.domains.billing.models import Subscription, SubscriptionTier, SubscriptionStatus
from app.domains.projects.models import Project, ProjectMember, ProjectRole
from app.domains.integrations.models import Integration, IntegrationStatus
from app.domains.products.models import Product
from app.domains.customers.models import CustomerProfile
from app.domains.orders.models import Order
from app.domains.messages.models import Message, MessageDirection
from scripts.meta_review_data import META_TEST_ACCOUNTS

REVIEWER_DEFAULT_PASSWORD = os.getenv("META_REVIEW_PASSWORD", "MetaReview2026!")


async def get_or_create_user(session: AsyncSession, acc_data: Dict[str, Any]) -> User:
    """Ensure reviewer user and active enterprise subscription exist."""
    res = await session.execute(select(User).where(User.email == acc_data["email"]))
    user = res.scalar_one_or_none()
    pwd_hash = get_password_hash(REVIEWER_DEFAULT_PASSWORD)

    if not user:
        user = User(
            email=acc_data["email"],
            password_hash=pwd_hash,
            name=acc_data["name"],
            role=UserRole.USER,
            is_active=True,
        )
        session.add(user)
        await session.flush()
    else:
        user.password_hash = pwd_hash
        user.name = acc_data["name"]
        user.is_active = True
        await session.flush()

    sub_res = await session.execute(select(Subscription).where(Subscription.user_id == user.id))
    sub = sub_res.scalar_one_or_none()
    if not sub:
        sub = Subscription(
            user_id=user.id,
            tier=SubscriptionTier.ENTERPRISE,
            status=SubscriptionStatus.ACTIVE,
            billing_cycle="annually",
            started_at=datetime.utcnow(),
        )
        session.add(sub)
        await session.flush()

    return user


async def get_or_create_project(session: AsyncSession, user: User, p_data: Dict[str, Any]) -> Project:
    """Ensure project and owner membership exist."""
    res = await session.execute(select(Project).where(Project.project_code == p_data["code"]))
    project = res.scalar_one_or_none()

    if not project:
        project = Project(
            owner_id=user.id,
            project_code=p_data["code"],
            name=p_data["name"],
            description=p_data["description"],
            bot_name=p_data.get("bot_name", "Alex"),
            bot_tone=p_data.get("bot_tone", "Professional"),
            personality_prompt=p_data.get("personality_prompt", ""),
            is_active=True,
            settings={"ai_enabled": True, "auto_response": True, "language": "en"},
        )
        session.add(project)
        await session.flush()

    mem_res = await session.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user.id,
        )
    )
    if not mem_res.scalar_one_or_none():
        session.add(ProjectMember(project_id=project.id, user_id=user.id, role=ProjectRole.OWNER))
        await session.flush()

    return project


async def seed_integrations(session: AsyncSession, project: Project, items: List[Dict[str, Any]]) -> None:
    """Seed or update connected Meta integrations."""
    for item in items:
        res = await session.execute(
            select(Integration).where(
                Integration.project_id == project.id,
                Integration.provider == item["provider"],
            )
        )
        integ = res.scalar_one_or_none()
        if not integ:
            integ = Integration(
                project_id=project.id,
                provider=item["provider"],
                status=IntegrationStatus.CONNECTED,
                config=item.get("config", {}),
                last_sync=datetime.utcnow(),
            )
            session.add(integ)
        else:
            integ.status = IntegrationStatus.CONNECTED
            integ.config = item.get("config", {})
            integ.last_sync = datetime.utcnow()
    await session.flush()


async def seed_catalog(session: AsyncSession, project: Project, products: List[Dict[str, Any]]) -> None:
    """Seed project products catalog."""
    for prod_info in products:
        res = await session.execute(
            select(Product).where(Product.project_id == project.id, Product.name == prod_info["name"])
        )
        if not res.scalar_one_or_none():
            session.add(Product(project_id=project.id, **prod_info))
    await session.flush()


async def seed_crm_and_interactions(
    session: AsyncSession,
    project: Project,
    customers_data: List[Dict[str, Any]],
    orders_data: List[Dict[str, Any]],
    messages_data: List[Dict[str, Any]],
) -> None:
    """Seed customers, recent orders, and simulated customer conversations."""
    saved_customers: List[CustomerProfile] = []
    for c_info in customers_data:
        res = await session.execute(
            select(CustomerProfile).where(
                CustomerProfile.project_id == project.id,
                CustomerProfile.customer_id == c_info["customer_id"],
            )
        )
        cust = res.scalar_one_or_none()
        if not cust:
            cust = CustomerProfile(project_id=project.id, **c_info)
            session.add(cust)
            await session.flush()
        saved_customers.append(cust)

    for o_info in orders_data:
        c_idx = o_info["customer_index"]
        c_profile = saved_customers[c_idx] if c_idx < len(saved_customers) else saved_customers[0]
        res = await session.execute(
            select(Order).where(Order.project_id == project.id, Order.external_id == o_info["external_id"])
        )
        if not res.scalar_one_or_none():
            session.add(
                Order(
                    project_id=project.id,
                    customer_id=c_profile.id,
                    external_id=o_info["external_id"],
                    provider=o_info["provider"],
                    status=o_info["status"],
                    total=o_info["total"],
                    order_date=datetime.utcnow() - timedelta(days=2),
                )
            )
    await session.flush()

    for idx, m_info in enumerate(messages_data):
        c_idx = m_info["customer_index"]
        c_profile = saved_customers[c_idx] if c_idx < len(saved_customers) else saved_customers[0]
        direction = MessageDirection.INBOUND if m_info["role"] == "user" else MessageDirection.OUTBOUND
        res = await session.execute(
            select(Message).where(Message.project_id == project.id, Message.content == m_info["content"])
        )
        if not res.scalar_one_or_none():
            session.add(
                Message(
                    project_id=project.id,
                    customer_id=c_profile.id,
                    direction=direction,
                    platform=m_info.get("platform", "instagram"),
                    provider=m_info.get("platform", "instagram"),
                    content=m_info["content"],
                    ai_generated=(m_info["role"] == "assistant"),
                    status="delivered",
                    created_at=datetime.utcnow() - timedelta(minutes=60 - idx * 10),
                )
            )
    await session.flush()


async def run_seed() -> None:
    """Execute complete database seeding for all 4 Meta Review accounts."""
    print("[*] Initializing Meta App Review test accounts seeding...")
    async with AsyncSessionLocal() as session:
        try:
            for item in META_TEST_ACCOUNTS:
                print(f"[+] Provisioning: {item['email']} ({item['project']['name']})...")
                user = await get_or_create_user(session, item)
                project = await get_or_create_project(session, user, item["project"])
                await seed_integrations(session, project, item["integrations"])
                await seed_catalog(session, project, item["products"])
                await seed_crm_and_interactions(
                    session, project, item["customers"], item["orders"], item["messages"]
                )
            await session.commit()
            print("[SUCCESS] ALL 4 META TEST ACCOUNTS SEEDED SUCCESSFULLY IN SUPABASE!")
        except Exception as err:
            await session.rollback()
            print(f"[ERROR] Seeding failed with error: {err}")
            raise


if __name__ == "__main__":
    asyncio.run(run_seed())
