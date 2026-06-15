"""
Script to create test data for AI Sales Commander.
Run this to populate your database with sample orders, messages, and projects.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from decimal import Decimal
import random

from sqlalchemy import select
from app.core.database import async_session_maker
from app.db.models import (
    User, Project, Order, Message, Integration,
    OrderStatus, MessageDirection, IntegrationProvider
)
from app.core.security import get_password_hash


async def create_test_user():
    """Create test user."""
    async with async_session_maker() as session:
        # Check if user exists
        result = await session.execute(
            select(User).where(User.email == "1111111@test.com")
        )
        user = result.scalar_one_or_none()
        
        if user:
            print("✅ Test user already exists")
            return user
        
        # Create user
        user = User(
            email="1111111@test.com",
            password_hash=get_password_hash("1111111"),
            full_name="Test User",
            is_active=True,
            is_superuser=False
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print("✅ Created test user: 1111111@test.com / 1111111")
        return user


async def create_test_project(user):
    """Create test project."""
    async with async_session_maker() as session:
        # Check if project exists
        result = await session.execute(
            select(Project).where(Project.owner_id == user.id)
        )
        project = result.scalar_one_or_none()
        
        if project:
            print("✅ Test project already exists")
            return project
        
        # Create project
        project = Project(
            owner_id=user.id,
            name="My E-Commerce Store",
            description="Sample online store for testing AI Sales Commander",
            settings={
                "currency": "USD",
                "timezone": "UTC",
                "auto_response": True,
                "ai_enabled": True
            },
            is_active=True
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        print(f"✅ Created test project: {project.name}")
        return project


async def create_test_orders(project):
    """Create sample orders."""
    async with async_session_maker() as session:
        # Check if orders exist
        result = await session.execute(
            select(Order).where(Order.project_id == project.id).limit(1)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("✅ Test orders already exist")
            return
        
        # Create 50 orders over the last 30 days
        statuses = [OrderStatus.PENDING, OrderStatus.PROCESSING, OrderStatus.FULFILLED, OrderStatus.CANCELLED]
        
        customers = [
            {"name": "John Smith", "email": "john@example.com", "phone": "+1234567890"},
            {"name": "Sarah Johnson", "email": "sarah@example.com", "phone": "+1234567891"},
            {"name": "Michael Brown", "email": "michael@example.com", "phone": "+1234567892"},
            {"name": "Emily Davis", "email": "emily@example.com", "phone": "+1234567893"},
            {"name": "David Wilson", "email": "david@example.com", "phone": "+1234567894"},
            {"name": "Lisa Anderson", "email": "lisa@example.com", "phone": "+1234567895"},
            {"name": "James Taylor", "email": "james@example.com", "phone": "+1234567896"},
            {"name": "Jennifer Martinez", "email": "jennifer@example.com", "phone": "+1234567897"},
            {"name": "Robert Garcia", "email": "robert@example.com", "phone": "+1234567898"},
            {"name": "Maria Rodriguez", "email": "maria@example.com", "phone": "+1234567899"}
        ]
        
        products = [
            {"name": "Wireless Headphones", "price": 79.99},
            {"name": "Smart Watch", "price": 299.99},
            {"name": "Laptop Stand", "price": 49.99},
            {"name": "USB-C Cable", "price": 19.99},
            {"name": "Phone Case", "price": 29.99},
            {"name": "Bluetooth Speaker", "price": 89.99},
            {"name": "Webcam HD", "price": 69.99},
            {"name": "Mechanical Keyboard", "price": 149.99},
            {"name": "Gaming Mouse", "price": 59.99},
            {"name": "Monitor 27\"", "price": 349.99}
        ]
        
        orders = []
        for i in range(50):
            # Random date in last 30 days
            days_ago = random.randint(0, 30)
            order_date = datetime.utcnow() - timedelta(days=days_ago)
            
            # Random customer
            customer = random.choice(customers)
            
            # Random products (1-3 items)
            num_items = random.randint(1, 3)
            selected_products = random.sample(products, num_items)
            
            line_items = [
                {
                    "name": product["name"],
                    "quantity": random.randint(1, 3),
                    "price": product["price"]
                }
                for product in selected_products
            ]
            
            total = sum(item["price"] * item["quantity"] for item in line_items)
            
            order = Order(
                project_id=project.id,
                external_id=f"ORD-{1000 + i}",
                customer_name=customer["name"],
                customer_email=customer["email"],
                customer_phone=customer["phone"],
                line_items=line_items,
                total=Decimal(str(total)),
                currency="USD",
                status=random.choice(statuses),
                provider="shopify",
                order_date=order_date,
                extra_data={
                    "shipping_address": "123 Main St, City, State 12345",
                    "payment_method": random.choice(["credit_card", "paypal", "stripe"])
                }
            )
            orders.append(order)
        
        session.add_all(orders)
        await session.commit()
        print(f"✅ Created {len(orders)} test orders")


async def create_test_messages(project):
    """Create sample messages."""
    async with async_session_maker() as session:
        # Check if messages exist
        result = await session.execute(
            select(Message).where(Message.project_id == project.id).limit(1)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("✅ Test messages already exist")
            return
        
        # Get some orders
        result = await session.execute(
            select(Order).where(Order.project_id == project.id).limit(10)
        )
        orders = result.scalars().all()
        
        if not orders:
            print("⚠️  No orders found, skipping messages")
            return
        
        # Sample customer messages
        customer_messages = [
            "When will my order arrive?",
            "Can I change my shipping address?",
            "I haven't received my order yet",
            "How do I track my order?",
            "Is my order shipped?",
            "Can I cancel my order?",
            "What's the status of my order?",
            "I need help with my order",
            "Can I add more items to my order?",
            "Is there a discount code available?"
        ]
        
        # Sample AI responses
        ai_responses = [
            "Your order is currently being processed and will ship within 2-3 business days.",
            "I can help you update your shipping address. Let me check your order details.",
            "I'll check the status of your order right away.",
            "You can track your order using the tracking link we sent to your email.",
            "Your order has been shipped! You should receive it soon.",
            "I can help you with the cancellation process.",
            "Let me get the latest status for you.",
            "I'm here to help! What specifically do you need assistance with?",
            "Unfortunately, orders cannot be modified after processing, but I can help you place a new order.",
            "Let me check for available promotions for you!"
        ]
        
        channels = ["whatsapp", "telegram", "instagram", "facebook"]
        
        messages = []
        for order in orders:
            # Create 2-4 messages per order
            num_messages = random.randint(2, 4)
            channel = random.choice(channels)
            
            for j in range(num_messages):
                # Customer message (inbound)
                customer_msg = Message(
                    project_id=project.id,
                    order_id=order.id,
                    customer_id=order.customer_email,
                    direction=MessageDirection.INBOUND,
                    content=random.choice(customer_messages),
                    channel=channel,
                    provider=channel,
                    created_at=order.order_date + timedelta(hours=j*2)
                )
                messages.append(customer_msg)
                
                # AI response (outbound)
                ai_msg = Message(
                    project_id=project.id,
                    order_id=order.id,
                    customer_id=order.customer_email,
                    direction=MessageDirection.OUTBOUND,
                    content=random.choice(ai_responses),
                    channel=channel,
                    provider=channel,
                    created_at=order.order_date + timedelta(hours=j*2, minutes=5),
                    extra_data={
                        "ai_generated": True,
                        "model": "gemini-1.5-pro",
                        "tokens_used": random.randint(100, 500),
                        "cost": random.uniform(0.001, 0.01)
                    }
                )
                messages.append(ai_msg)
        
        session.add_all(messages)
        await session.commit()
        print(f"✅ Created {len(messages)} test messages")


async def create_test_integrations(project):
    """Create sample integrations."""
    async with async_session_maker() as session:
        # Check if integrations exist
        result = await session.execute(
            select(Integration).where(Integration.project_id == project.id).limit(1)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("✅ Test integrations already exist")
            return
        
        integrations = [
            Integration(
                project_id=project.id,
                provider=IntegrationProvider.SHOPIFY,
                config={
                    "shop_url": "demo-store.myshopify.com",
                    "access_token": "demo_token_12345"
                },
                is_active=True,
                last_sync=datetime.utcnow() - timedelta(hours=2)
            ),
            Integration(
                project_id=project.id,
                provider=IntegrationProvider.WHATSAPP,
                config={
                    "phone_number": "+1234567890",
                    "api_key": "demo_whatsapp_key"
                },
                is_active=True,
                last_sync=datetime.utcnow() - timedelta(minutes=30)
            ),
            Integration(
                project_id=project.id,
                provider=IntegrationProvider.TELEGRAM,
                config={
                    "bot_token": "demo_telegram_token",
                    "bot_username": "demo_bot"
                },
                is_active=True,
                last_sync=datetime.utcnow() - timedelta(hours=1)
            )
        ]
        
        session.add_all(integrations)
        await session.commit()
        print(f"✅ Created {len(integrations)} test integrations")


async def main():
    """Main function to create all test data."""
    print("\n🚀 Creating test data for AI Sales Commander...\n")
    
    try:
        # Create test user
        user = await create_test_user()
        
        # Create test project
        project = await create_test_project(user)
        
        # Create test orders
        await create_test_orders(project)
        
        # Create test messages
        await create_test_messages(project)
        
        # Create test integrations
        await create_test_integrations(project)
        
        print("\n✨ Test data creation complete!")
        print("\n📋 Summary:")
        print(f"   User: 1111111@test.com / 1111111")
        print(f"   Project: {project.name}")
        print(f"   Project ID: {project.id}")
        print("\n🎉 You can now login and explore the platform!\n")
        
    except Exception as e:
        print(f"\n❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
