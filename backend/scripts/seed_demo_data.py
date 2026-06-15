import asyncio
import os
import sys
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Base and models to ensure they are registered with Base.metadata
from app.db.models import User, Project, Product, Order, CustomerProfile, Message, MessageDirection, UserRole, Base
from app.core.security import get_password_hash
from app.core.config import settings

# Database setup
# Note: statement_cache_size=0 is required for pgbouncer (Supabase)
DATABASE_URL = "postgresql+asyncpg://postgres.mrwmqimafmpywckflpoi:ana_b7b_noranty@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"statement_cache_size": 0}
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def seed_demo_data():
    print("🌱 Starting professional demo data seeding...")
    
    # 0. Initialize Tables (if they don't exist)
    print("🏗️ Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables ready.")

    async with AsyncSessionLocal() as db:
        try:
            # 1. Ensure Demo User exists
            print("👤 Checking for test user...")
            result = await db.execute(select(User).where(User.email == "test@aisales.local"))
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    email="test@aisales.local",
                    password_hash=get_password_hash("AiSales2024!Demo"),
                    name="Meta Reviewer",
                    role=UserRole.ADMIN,
                    is_active=True
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
                print("✅ Created test user: test@aisales.local")
            else:
                print("✅ Test user already exists.")

            # 2. Ensure Demo Project exists
            print("📂 Checking for demo project...")
            result = await db.execute(select(Project).where(Project.owner_id == user.id, Project.name == "Elegant Tech Store"))
            project = result.scalar_one_or_none()
            if not project:
                project = Project(
                    owner_id=user.id,
                    name="Elegant Tech Store",
                    project_code="ELEGANT-TECH-001",
                    description="Professional electronics and lifestyle accessories store.",
                    timezone="UTC",
                    settings={
                        "ai_enabled": True,
                        "auto_response": True,
                        "language": "en",
                        "ai_persona": {
                            "bot_name": "Alex",
                            "tone": "professional"
                        }
                    },
                    is_active=True
                )
                db.add(project)
                await db.commit()
                await db.refresh(project)
                print("✅ Created project: Elegant Tech Store")
            else:
                print("✅ Demo project already exists.")

            # 3. Seed Professional Products
            print("📦 Seeding products...")
            products_data = [
                {
                    "name": "Smart Watch Pro X",
                    "description": "Premium fitness tracker with heart rate monitoring, GPS, and 7-day battery life.",
                    "sku": "SW-PRO-001",
                    "price": 199.99,
                    "category": "Wearables",
                    "stock_quantity": 45,
                    "images": ["https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800&auto=format&fit=crop"]
                },
                {
                    "name": "Sonic Earbuds",
                    "description": "Noise-cancelling wireless earbuds with crystal clear audio and ergonomic design.",
                    "sku": "SE-2024",
                    "price": 129.50,
                    "category": "Audio",
                    "stock_quantity": 120,
                    "images": ["https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop"]
                },
                {
                    "name": "Ultra-Slim Power Bank",
                    "description": "10,000mAh portable charger, fast charging support for multiple devices.",
                    "sku": "PB-SLIM-10",
                    "price": 45.00,
                    "category": "Accessories",
                    "stock_quantity": 8,
                    "images": ["https://images.unsplash.com/photo-1609592424089-980453733075?w=800&auto=format&fit=crop"]
                },
                {
                    "name": "Crystal 4K Monitor",
                    "description": "27-inch 4K UHD display with HDR10 for vibrant colors and sharp detail.",
                    "sku": "MON-4K-27",
                    "price": 349.99,
                    "category": "Computing",
                    "stock_quantity": 25,
                    "images": ["https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop"]
                }
            ]

            for p_info in products_data:
                res = await db.execute(select(Product).where(Product.project_id == project.id, Product.name == p_info["name"]))
                if not res.scalar_one_or_none():
                    prod = Product(project_id=project.id, **p_info)
                    db.add(prod)
            
            await db.commit()
            print("✅ Products seeded.")

            # 4. Seed Mock Customers
            print("👥 Seeding customer profiles...")
            customers_data = [
                {
                    "customer_id": "meta_reviewer_test",
                    "name": "Alex Reviewer",
                    "email": "reviewer@meta.com",
                    "phone": "+15550199",
                    "customer_type": "vip",
                    "avatar_url": "https://i.pravatar.cc/150?u=alex"
                },
                {
                    "customer_id": "sarah_jones_mock",
                    "name": "Sarah Jones",
                    "email": "sarah.j@example.com",
                    "phone": "+15550200",
                    "customer_type": "regular",
                    "avatar_url": "https://i.pravatar.cc/150?u=sarah"
                }
            ]

            customers = []
            for c_info in customers_data:
                res = await db.execute(select(CustomerProfile).where(CustomerProfile.project_id == project.id, CustomerProfile.customer_id == c_info["customer_id"]))
                cust = res.scalar_one_or_none()
                if not cust:
                    cust = CustomerProfile(project_id=project.id, **c_info)
                    db.add(cust)
                    await db.flush()
                customers.append(cust)
            
            await db.commit()
            print("✅ Customers seeded.")

            # 5. Seed Mock Orders
            print("🛒 Seeding orders...")
            orders_data = [
                {
                    "customer_id": customers[0].id,
                    "external_id": "ORD-1001",
                    "provider": "ai_agent",
                    "status": "delivered",
                    "total": 199.99,
                    "order_date": datetime.utcnow() - timedelta(days=5)
                },
                {
                    "customer_id": customers[1].id,
                    "external_id": "ORD-1002",
                    "provider": "shopify",
                    "status": "processing",
                    "total": 129.50,
                    "order_date": datetime.utcnow() - timedelta(days=1)
                }
            ]

            for o_info in orders_data:
                res = await db.execute(select(Order).where(Order.project_id == project.id, Order.external_id == o_info["external_id"]))
                if not res.scalar_one_or_none():
                    order = Order(project_id=project.id, **o_info)
                    db.add(order)
            
            await db.commit()
            print("✅ Orders seeded.")

            # 6. Seed Simulated Conversation
            print("💬 Seeding simulation messages...")
            convo_messages = [
                {"role": "user", "content": "Hi, I'm interested in the Smart Watch Pro X. Is it in stock?", "customer": customers[0]},
                {"role": "assistant", "content": "Hello! Yes, the Smart Watch Pro X is currently in stock ⌚. We have plenty available for immediate shipping!", "customer": customers[0]},
                {"role": "user", "content": "How long does the battery last?", "customer": customers[0]},
                {"role": "assistant", "content": "It features an impressive 7-day battery life on a single charge 🔋! It's perfect for tracking your fitness all week.", "customer": customers[0]}
            ]

            for i, m_info in enumerate(convo_messages):
                msg_content = m_info["content"]
                res = await db.execute(select(Message).where(Message.project_id == project.id, Message.content == msg_content))
                if not res.scalar_one_or_none():
                    msg = Message(
                        project_id=project.id,
                        customer_id=m_info["customer"].id,
                        direction=MessageDirection.INBOUND if m_info["role"] == "user" else MessageDirection.OUTBOUND,
                        platform="instagram",
                        provider="meta",
                        content=msg_content,
                        status="sent",
                        created_at=datetime.utcnow() - timedelta(minutes=60 - i*10)
                    )
                    db.add(msg)
            
            await db.commit()
            print("✅ Simulated messages seeded.")

            print("\n🌟 ALL DEMO DATA SEEDED SUCCESSFULLY!")
            print("🚀 You can now log in with: test@aisales.local / AiSales2024!Demo")
            print("📊 Project 'Elegant Tech Store' is ready for your screencasts.")

        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
