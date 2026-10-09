import pytest
import asyncio
from uuid import uuid4
from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.db.models import Project, User
from app.domains.customers.models import CustomerProfile
from app.domains.messages.models import Message
from app.services.webhook_processor import WebhookProcessor
from app.services.webhook_domain import NormalizedMessage
from app.core.context import ServiceContext
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_webhook_concurrency_idempotency():
    '''Test that concurrent webhooks for the same new user do not create duplicate CustomerProfiles.'''
    
    project_id = uuid4()
    user_id = uuid4()
    
    async with AsyncSessionLocal() as db_session:
        # Create user and project
        user = User(id=user_id, email=f"test_{uuid4().hex[:8]}@example.com", password_hash="hashed")
        db_session.add(user)
        await db_session.commit()
        
        project = Project(id=project_id, owner_id=user_id, project_code=f"TEST_{uuid4().hex[:4]}", name="Test")
        db_session.add(project)
        await db_session.commit()

    sender_id = f"concurrent_user_{uuid4().hex[:8]}"
    
    # Create a mock background_tasks
    mock_bg = MagicMock()
    mock_bg.add_task = MagicMock()
    
    processor = WebhookProcessor(db_session, mock_bg)
    
    # Create two identical but distinct webhook events (same sender, different message)
    # Simulating a user sending two messages very fast
    context = ServiceContext(
        service_name="webhook_gateway",
        project_id=project_id,
        operation="process_event"
    )
    
    msg1 = NormalizedMessage(
        external_id=f"msg_1_{uuid4().hex[:8]}",
        content="Hello!",
        sender_id=sender_id,
        sender_name="Concurrent User",
        platform="whatsapp",
        provider="meta",
        media_type="text",
        extra_data={},
        is_from_me=False
    )
    
    msg2 = NormalizedMessage(
        external_id=f"msg_2_{uuid4().hex[:8]}",
        content="Are you there?",
        sender_id=sender_id,
        sender_name="Concurrent User",
        platform="whatsapp",
        provider="meta",
        media_type="text",
        extra_data={},
        is_from_me=False
    )
    
    # Run them concurrently with separate db sessions
    async def process_msg(msg):
        async with AsyncSessionLocal() as session:
            proc = WebhookProcessor(session, mock_bg)
            return await proc.process_message(context, msg)
            
    await asyncio.gather(
        process_msg(msg1),
        process_msg(msg2)
    )
    
    # Verify exactly one customer profile was created
    query_customers = select(CustomerProfile).where(
        CustomerProfile.project_id == project_id,
        CustomerProfile.customer_id == sender_id
    )
    result = await db_session.execute(query_customers)
    customers = result.scalars().all()
    
    assert len(customers) == 1, f"Expected 1 customer, got {len(customers)}"
    customer = customers[0]
    
    # Verify two messages were saved and linked to the SAME customer
    query_messages = select(Message).where(
        Message.project_id == project_id,
        Message.customer_id == customer.id
    )
    result_msgs = await db_session.execute(query_messages)
    messages = result_msgs.scalars().all()
    
    assert len(messages) == 2, f"Expected 2 messages, got {len(messages)}"
    
    # Test identical event retry idempotency (same external_id)
    msg1_retry = NormalizedMessage(
        external_id=msg1.external_id, # Same as first
        content="Hello!",
        sender_id=sender_id,
        sender_name="Concurrent User",
        platform="whatsapp",
        provider="meta",
        media_type="text",
        extra_data={},
        is_from_me=False
    )
    
    res = await processor.process_message(context, msg1_retry)
    assert res["status"] == "skipped"
    assert res["reason"] == "duplicate_external_id"
    
    # Verify no new message was inserted
    result_msgs_after = await db_session.execute(query_messages)
    assert len(result_msgs_after.scalars().all()) == 2

    # Clean up with raw SQL to avoid cascade errors on missing tables
    from sqlalchemy import text
    await db_session.execute(text("DELETE FROM customer_profiles WHERE project_id = :p"), {"p": project_id})
    await db_session.execute(text("DELETE FROM messages WHERE project_id = :p"), {"p": project_id})
    await db_session.execute(text("DELETE FROM projects WHERE id = :p"), {"p": project_id})
    await db_session.execute(text("DELETE FROM users WHERE id = :u"), {"u": user_id})
    await db_session.commit()
