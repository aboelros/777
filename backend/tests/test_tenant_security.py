from datetime import timezone, datetime
import pytest
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import app.main  # Important: forces SQLAlchemy registry to load all models first
from app.db.models import User
from app.db.models import Project, ProjectMember
from app.db.models import Message, MessageDirection
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context
from app.domains.messages.repository import MessageRepository

from app.core.database import AsyncSessionLocal

@pytest.mark.asyncio
async def test_tenant_context_resolution_success():
    user_id = uuid4()
    project_id = uuid4()

    async with AsyncSessionLocal() as db:
        # Create User A
        user = User(id=user_id, email=f"test_{user_id}@example.com", password_hash="hash", role="admin")
        db.add(user)

        # Create Project A
        project = Project(id=project_id, owner_id=user_id, project_code=f"PRJ_{project_id}", name="Test Project", timezone="UTC")
        db.add(project)

        # Create User B
        user_b_id = uuid4()
        user_b = User(id=user_b_id, email=f"test_{user_b_id}@example.com", password_hash="hash", role="admin")
        db.add(user_b)

        # Create Project B
        project_b_id = uuid4()
        project_b = Project(id=project_b_id, owner_id=user_b_id, project_code=f"PRJ_{project_b_id}", name="Project B", timezone="UTC")
        db.add(project_b)

        await db.commit()

        # POSITIVE CONTROL: User A + Project A -> Success
        context = await get_tenant_context(project_id=project_id, user_id=str(user_id), db=db)
        assert isinstance(context, TenantContext)
        assert context.project_id == project_id
        assert context.user_id == user_id
        assert context.role == "owner"

        # POSITIVE CONTROL: User B + Project B -> Success
        context_b = await get_tenant_context(project_id=project_b_id, user_id=str(user_b_id), db=db)
        assert isinstance(context_b, TenantContext)
        assert context_b.project_id == project_b_id

        # NEGATIVE CONTROL: User A + Random UUID -> 404
        random_project_id = uuid4()
        with pytest.raises(HTTPException) as exc:
            await get_tenant_context(project_id=random_project_id, user_id=str(user_id), db=db)
        assert exc.value.status_code == 404

        # NEGATIVE CONTROL: User A + Project B -> 404
        with pytest.raises(HTTPException) as exc_b:
            await get_tenant_context(project_id=project_b_id, user_id=str(user_id), db=db)
        assert exc_b.value.status_code == 404

@pytest.mark.asyncio
async def test_tenant_a_to_tenant_b_project_denied():
    pass  # Retained for future or replaced by above test

@pytest.mark.asyncio
async def test_api_conversations_endpoint():
    """Test the migrated messaging endpoint logic directly."""
    from app.core.security import get_current_user_id

    user_a_id = uuid4()
    project_a_id = uuid4()
    user_b_id = uuid4()
    project_b_id = uuid4()

    async with AsyncSessionLocal() as db:
        # Create User A
        user_a = User(id=user_a_id, email=f"test_{user_a_id}@example.com", password_hash="hash", role="admin")
        project_a = Project(id=project_a_id, owner_id=user_a_id, project_code=f"PRJ_{project_a_id}", name="Project A", timezone="UTC")
        db.add_all([user_a, project_a])

        # Create User B
        user_b = User(id=user_b_id, email=f"test_{user_b_id}@example.com", password_hash="hash", role="admin")
        project_b = Project(id=project_b_id, owner_id=user_b_id, project_code=f"PRJ_{project_b_id}", name="Project B", timezone="UTC")
        db.add_all([user_b, project_b])

        # Create a message in Project B
        from app.db.models import CustomerProfile
        customer_b_id = uuid4()
        customer_b = CustomerProfile(id=customer_b_id, project_id=project_b_id, customer_id="test_platform_id_b", name="Test Customer B")

        msg_b = Message(
            id=uuid4(), project_id=project_b_id, customer_id=customer_b_id, direction=MessageDirection.INBOUND,
            platform="whatsapp", provider="whatsapp", content="Secret message"
        )
        db.add_all([customer_b, msg_b])
        await db.commit()

    from httpx import AsyncClient
    from app.main import app
    from app.core.security import create_access_token

    # Generate real JWTs
    token_a = create_access_token({"sub": str(user_a_id)})
    token_b = create_access_token({"sub": str(user_b_id)})

    async def make_request(token, target_project_id):
        headers = {"Authorization": f"Bearer {token}"}
        # Explicitly hitting the FastAPI app to traverse the full middleware & auth stack
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(f"/api/v1/messages/{target_project_id}/conversations", headers=headers)
        return response

    # 1. Valid Tenant A request
    res_a = await make_request(token_a, project_a_id)
    assert res_a.status_code == 200

    # 2. Tenant A -> Tenant B project attack
    res_attack = await make_request(token_a, project_b_id)
    assert res_attack.status_code == 404

    # 3. Valid Tenant B request (should succeed)
    res_b = await make_request(token_b, project_b_id)
    assert res_b.status_code == 200

    # 4. Tenant A JWT + Project A URL + Tenant B conversation -> 404 (or empty)
    # Target endpoint: /api/v1/messages/{project_id}/conversations/{conversation_id}/messages
    async def make_msg_request(token, target_project_id, conv_id):
        headers = {"Authorization": f"Bearer {token}"}
        async with AsyncClient(app=app, base_url="http://test") as client:
            return await client.get(
                f"/api/v1/messages/{target_project_id}/conversations/{conv_id}/messages",
                headers=headers
            )

    # The conversation_id derived for Tenant B's message:
    conv_id_b = str(customer_b_id)

    # Attack: User A tries to get User B's conversation through Project A's URL
    res_attack_msg = await make_msg_request(token_a, project_a_id, conv_id_b)
    # The endpoint returns a list of matched messages. Should be empty because the repo limits to Project A!
    assert res_attack_msg.status_code == 200
    assert len(res_attack_msg.json()) == 0

    # Valid: User B getting User B's conversation
    res_valid_msg = await make_msg_request(token_b, project_b_id, conv_id_b)
    assert res_valid_msg.status_code == 200
    assert len(res_valid_msg.json()) == 1

@pytest.mark.asyncio
async def test_api_customer_profile_endpoint():
    """Test the migrated customer profile endpoint."""
    from httpx import AsyncClient
    from app.main import app
    from app.core.security import create_access_token

    user_a_id = uuid4()
    project_a_id = uuid4()
    user_b_id = uuid4()
    project_b_id = uuid4()

    async with AsyncSessionLocal() as db:
        # User A & Project A
        user_a = User(id=user_a_id, email=f"test_{user_a_id}@example.com", password_hash="hash", role="admin")
        project_a = Project(id=project_a_id, owner_id=user_a_id, project_code=f"PRJ_{project_a_id}", name="Project A", timezone="UTC")

        # User B & Project B
        user_b = User(id=user_b_id, email=f"test_{user_b_id}@example.com", password_hash="hash", role="admin")
        project_b = Project(id=project_b_id, owner_id=user_b_id, project_code=f"PRJ_{project_b_id}", name="Project B", timezone="UTC")

        from app.db.models import CustomerProfile

        # Profile for A
        profile_a_id = uuid4()
        profile_a = CustomerProfile(id=profile_a_id, project_id=project_a_id, customer_id="A", name="A")

        # Profile for B
        profile_b_id = uuid4()
        profile_b = CustomerProfile(id=profile_b_id, project_id=project_b_id, customer_id="B", name="B")

        db.add_all([user_a, project_a, user_b, project_b, profile_a, profile_b])
        await db.commit()

    token_a = create_access_token({"sub": str(user_a_id)})
    token_b = create_access_token({"sub": str(user_b_id)})

    async def make_profile_request(token, target_project_id, target_profile_id):
        headers = {"Authorization": f"Bearer {token}"}
        async with AsyncClient(app=app, base_url="http://test") as client:
            return await client.get(f"/api/v1/messages/{target_project_id}/customers/{target_profile_id}", headers=headers)

    # Matrix:
    # 1. A + A project + A profile -> 200
    r1 = await make_profile_request(token_a, project_a_id, profile_a_id)
    assert r1.status_code == 200

    # 2. B + B project + B profile -> 200
    r2 = await make_profile_request(token_b, project_b_id, profile_b_id)
    assert r2.status_code == 200

    # 3. A + B project -> 404 (Denied at project level)
    r3 = await make_profile_request(token_a, project_b_id, profile_b_id)
    assert r3.status_code == 404

    # 4. A + A project + B profile -> 404 (Denied at resource ownership level)
    r4 = await make_profile_request(token_a, project_a_id, profile_b_id)
    assert r4.status_code == 404

    # 5. A + A project + random profile -> 404
    r5 = await make_profile_request(token_a, project_a_id, uuid4())
    assert r5.status_code == 404

@pytest.mark.asyncio
async def test_tenant_a_project_to_tenant_b_resource_denied():
    async with AsyncSessionLocal() as db:
        # Setup Tenant A
        user_a_id = uuid4()
        user_a = User(id=user_a_id, email=f"test_{user_a_id}@example.com", password_hash="hash", role="admin")
        project_a_id = uuid4()
        project_a = Project(id=project_a_id, owner_id=user_a_id, project_code=f"PRJ_{project_a_id}", name="Project A", timezone="UTC")

        # Setup Tenant B
        user_b_id = uuid4()
        user_b = User(id=user_b_id, email=f"test_{user_b_id}@example.com", password_hash="hash", role="admin")
        project_b_id = uuid4()
        project_b = Project(id=project_b_id, owner_id=user_b_id, project_code=f"PRJ_{project_b_id}", name="Project B", timezone="UTC")

        # Create Message belonging to Project B
        message_b_id = uuid4()
        message_b = Message(
            id=message_b_id,
            project_id=project_b_id,
            direction=MessageDirection.INBOUND,
            platform="whatsapp",
            provider="whatsapp",
            content="Hello from B"
        )

        db.add_all([user_a, project_a, user_b, project_b, message_b])
        await db.commit()

        # User A successfully gets their own context
        context_a = await get_tenant_context(project_id=project_a_id, user_id=str(user_a_id), db=db)

        # User A tries to fetch Message B using their valid context
        repo = MessageRepository(db)
        result = await repo.get_message_by_context(context_a, message_b_id)

        # Must be denied (return None) because the repository enforces the chain:
        # resource.project_id == context.project_id
        assert result is None
@pytest.mark.asyncio
async def test_api_inbox_endpoint():
    """Test the GET /inbox endpoint."""
    from httpx import AsyncClient
    from app.main import app
    from app.core.security import create_access_token
    from app.db.models import CustomerProfile
    from app.db.models import Message
    from sqlalchemy import select

    user_a_id = uuid4()
    project_a_id = uuid4()

    user_b_id = uuid4()
    project_b_id = uuid4()

    async with AsyncSessionLocal() as db:
        # A
        user_a = User(id=user_a_id, email=f"test_{user_a_id}@example.com", password_hash="hash", role="admin")
        db.add(user_a)
        project_a = Project(id=project_a_id, owner_id=user_a_id, project_code=f"PRJ_{project_a_id}", name="A")
        db.add(project_a)
        member_a = ProjectMember(project_id=project_a_id, user_id=user_a_id, role="owner")
        db.add(member_a)

        customer_a_id = uuid4()
        customer_a = CustomerProfile(id=customer_a_id, project_id=project_a_id, name="A", customer_id="cust_a")
        db.add(customer_a)

        msg_a_id = uuid4()
        msg_a = Message(
            id=msg_a_id,
            project_id=project_a_id,
            customer_id=customer_a_id,
            content="Hello A",
            direction=MessageDirection.INBOUND,
            provider="whatsapp",
            platform="whatsapp",
            is_read=False,
            sender={"phone": "123"}
        )
        db.add(msg_a)

        # B
        user_b = User(id=user_b_id, email=f"test_{user_b_id}@example.com", password_hash="hash", role="admin")
        db.add(user_b)
        project_b = Project(id=project_b_id, owner_id=user_b_id, project_code=f"PRJ_{project_b_id}", name="B")
        db.add(project_b)
        member_b = ProjectMember(project_id=project_b_id, user_id=user_b_id, role="owner")
        db.add(member_b)

        customer_b_id = uuid4()
        customer_b = CustomerProfile(id=customer_b_id, project_id=project_b_id, name="B", customer_id="cust_b")
        db.add(customer_b)

        msg_b_id = uuid4()
        msg_b = Message(
            id=msg_b_id,
            project_id=project_b_id,
            customer_id=customer_b_id,
            content="Hello B",
            direction=MessageDirection.INBOUND,
            provider="whatsapp",
            platform="whatsapp",
            is_read=False,
            sender={"phone": "999"}
        )
        db.add(msg_b)

        await db.commit()

    token_a = create_access_token({"sub": str(user_a_id)})
    headers_a = {"Authorization": f"Bearer {token_a}"}

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Case A: Same tenant success
        res = await client.get(f"/api/v1/messages/{project_a_id}/inbox", headers=headers_a)
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["id"] == str(msg_a_id)
        assert data[0]["content"] == "Hello A"

        # Case B: Wrong project (Cross-tenant access) -> denied by TenantContext (404/403)
        res = await client.get(f"/api/v1/messages/{project_b_id}/inbox", headers=headers_a)
        assert res.status_code in (404, 403)





from uuid import uuid4
import pytest
from httpx import AsyncClient
from app.main import app
from app.core.security import create_access_token
from app.db.models import Project, User, Message, MessageDirection, CustomerProfile, Order, OrderStatus
from app.core.database import AsyncSessionLocal

@pytest.mark.asyncio
async def test_api_mark_conversation_read_endpoint():
    user_a_id, project_a_id = uuid4(), uuid4()
    user_b_id, project_b_id = uuid4(), uuid4()
    customer_b_id = uuid4()

    async with AsyncSessionLocal() as db:
        user_a = User(id=user_a_id, email=f"test_{user_a_id}@example.com", password_hash="hash", role="admin")
        project_a = Project(id=project_a_id, owner_id=user_a_id, project_code=f"PRJ_{project_a_id}", name="Project A", timezone="UTC")
        user_b = User(id=user_b_id, email=f"test_{user_b_id}@example.com", password_hash="hash", role="admin")
        project_b = Project(id=project_b_id, owner_id=user_b_id, project_code=f"PRJ_{project_b_id}", name="Project B", timezone="UTC")
        customer_b = CustomerProfile(id=customer_b_id, project_id=project_b_id, customer_id="CUST_B", name="Customer B")

        msg_b = Message(
            id=uuid4(), project_id=project_b_id, customer_id=customer_b_id, direction=MessageDirection.INBOUND,
            platform="whatsapp", provider="whatsapp", content="Secret message", is_read=False
        )

        db.add_all([user_a, project_a, user_b, project_b, customer_b, msg_b])
        await db.commit()

    token_a = create_access_token({'sub': str(user_a_id)})

    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=True), base_url='http://test') as client:
        # Cross tenant attempt
        headers = {'Authorization': f'Bearer {token_a}'}
        r = await client.patch(f'/api/v1/messages/{project_a_id}/conversations/{str(customer_b_id)}/read', headers=headers)
        assert r.status_code == 404

@pytest.mark.asyncio
async def test_api_toggle_customer_ai_endpoint():
    user_a_id, project_a_id = uuid4(), uuid4()
    user_b_id, project_b_id = uuid4(), uuid4()
    customer_b_id = uuid4()

    async with AsyncSessionLocal() as db:
        user_a = User(id=user_a_id, email=f"test_{user_a_id}@example.com", password_hash="hash", role="admin")
        project_a = Project(id=project_a_id, owner_id=user_a_id, project_code=f"PRJ_{project_a_id}", name="Project A", timezone="UTC")
        user_b = User(id=user_b_id, email=f"test_{user_b_id}@example.com", password_hash="hash", role="admin")
        project_b = Project(id=project_b_id, owner_id=user_b_id, project_code=f"PRJ_{project_b_id}", name="Project B", timezone="UTC")

        customer_b = CustomerProfile(id=customer_b_id, project_id=project_b_id, customer_id="CUST_B")
        db.add_all([user_a, project_a, user_b, project_b, customer_b])
        await db.commit()

    token_a = create_access_token({'sub': str(user_a_id)})
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=True), base_url='http://test') as client:
        headers = {'Authorization': f'Bearer {token_a}'}
        r = await client.patch(f'/api/v1/messages/{project_a_id}/customers/{str(customer_b_id)}/toggle-ai?enabled=true', headers=headers)
        assert r.status_code == 404

@pytest.mark.asyncio
async def test_api_send_message_endpoint():
    user_a_id, project_a_id = uuid4(), uuid4()
    user_b_id, project_b_id = uuid4(), uuid4()
    customer_b_id = uuid4()
    order_b_id = uuid4()

    async with AsyncSessionLocal() as db:
        user_a = User(id=user_a_id, email=f"test_{user_a_id}@example.com", password_hash="hash", role="admin")
        project_a = Project(id=project_a_id, owner_id=user_a_id, project_code=f"PRJ_{project_a_id}", name="Project A", timezone="UTC")
        user_b = User(id=user_b_id, email=f"test_{user_b_id}@example.com", password_hash="hash", role="admin")
        project_b = Project(id=project_b_id, owner_id=user_b_id, project_code=f"PRJ_{project_b_id}", name="Project B", timezone="UTC")
        customer_b = CustomerProfile(id=customer_b_id, project_id=project_b_id, customer_id="CUST_B")
        order_b = Order(id=order_b_id, project_id=project_b_id, customer_id=customer_b_id, external_id="ext", provider="shopify")
        db.add_all([user_a, project_a, user_b, project_b, customer_b, order_b])
        await db.commit()

    token_a = create_access_token({'sub': str(user_a_id)})
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=True), base_url='http://test') as client:
        headers = {'Authorization': f'Bearer {token_a}'}
        req = {"recipient": {"phone": "1234"}, "content": "hello", "provider": "whatsapp", "order_id": str(order_b_id)}
        r = await client.post(f'/api/v1/messages/{project_a_id}/send', json=req, headers=headers)
        assert r.status_code == 404

@pytest.mark.asyncio
async def test_api_delete_conversation_endpoint():
    user_a_id, project_a_id = uuid4(), uuid4()
    user_b_id, project_b_id = uuid4(), uuid4()
    customer_b_id = uuid4()

    async with AsyncSessionLocal() as db:
        user_a = User(id=user_a_id, email=f"test_{user_a_id}@example.com", password_hash="hash", role="admin")
        project_a = Project(id=project_a_id, owner_id=user_a_id, project_code=f"PRJ_{project_a_id}", name="Project A", timezone="UTC")
        user_b = User(id=user_b_id, email=f"test_{user_b_id}@example.com", password_hash="hash", role="admin")
        project_b = Project(id=project_b_id, owner_id=user_b_id, project_code=f"PRJ_{project_b_id}", name="Project B", timezone="UTC")
        customer_b = CustomerProfile(id=customer_b_id, project_id=project_b_id, customer_id="CUST_B")
        db.add_all([user_a, project_a, user_b, project_b, customer_b])
        await db.commit()

    token_a = create_access_token({'sub': str(user_a_id)})
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=True), base_url='http://test') as client:
        headers = {'Authorization': f'Bearer {token_a}'}
        r = await client.delete(f'/api/v1/messages/{project_a_id}/conversations/{str(customer_b_id)}', headers=headers)
        if r.status_code != 200: print(f'ERROR: {r.text}')
        assert r.status_code == 200
        assert r.json() == {"deleted_count": 0, "message": "Successfully deleted 0 messages", "status": "success"}

@pytest.mark.asyncio
async def test_api_orders_security():
    user_a_id, project_a_id = uuid4(), uuid4()
    user_b_id, project_b_id = uuid4(), uuid4()
    order_a_id = uuid4()
    order_b_id = uuid4()
    customer_a_id = uuid4()
    customer_b_id = uuid4()

    async with AsyncSessionLocal() as db:
        user_a = User(id=user_a_id, email=f"test_{user_a_id}@example.com", password_hash="hash", role="admin")
        project_a = Project(id=project_a_id, owner_id=user_a_id, project_code=f"PRJ_{project_a_id}", name="Project A", timezone="UTC")
        customer_a = CustomerProfile(id=customer_a_id, project_id=project_a_id, customer_id="CUST_A")
        order_a = Order(id=order_a_id, project_id=project_a_id, customer_id=customer_a_id, external_id="ext_A", provider="shopify", status="pending", total=100, order_date=datetime.now(timezone.utc))

        user_b = User(id=user_b_id, email=f"test_{user_b_id}@example.com", password_hash="hash", role="admin")
        project_b = Project(id=project_b_id, owner_id=user_b_id, project_code=f"PRJ_{project_b_id}", name="Project B", timezone="UTC")
        customer_b = CustomerProfile(id=customer_b_id, project_id=project_b_id, customer_id="CUST_B")
        order_b = Order(id=order_b_id, project_id=project_b_id, customer_id=customer_b_id, external_id="ext_B", provider="shopify", status="pending", total=100)

        db.add_all([user_a, project_a, customer_a, order_a, user_b, project_b, customer_b, order_b])
        await db.commit()

    token_a = create_access_token({'sub': str(user_a_id)})
    headers = {'Authorization': f'Bearer {token_a}'}

    async with AsyncClient(app=app, base_url='http://test') as client:
        # READ
        r = await client.get(f'/api/v1/orders/{project_a_id}/{order_a_id}', headers=headers)
        assert r.status_code == 200
        assert "metadata" in r.json()
        assert "extra_data" not in r.json()

        r = await client.get(f'/api/v1/orders/{project_a_id}/{order_b_id}', headers=headers)
        assert r.status_code == 404

        # CREATE
        r_create = await client.post(
            f"/api/v1/orders/{project_a_id}",
            json={
                "external_id": "ext_C",
                "provider": "shopify",
                "customer_id": str(customer_a_id),
                "metadata": {"custom": True},
            },
            headers=headers,
        )

        assert r_create.status_code == 201, r_create.text
        assert r_create.json()["metadata"] == {"custom": True}
        assert "extra_data" not in r_create.json()

        # UPDATE
        r = await client.patch(f'/api/v1/orders/{project_a_id}/{order_a_id}', json={"status": "processing"}, headers=headers)
        assert r.status_code == 200

        r = await client.patch(f'/api/v1/orders/{project_a_id}/{order_b_id}', json={"status": "processing"}, headers=headers)
        assert r.status_code == 404

        # DELETE
        r = await client.delete(f'/api/v1/orders/{project_a_id}/{order_b_id}', headers=headers)
        assert r.status_code == 404

        # COLLECTIONS
        r = await client.get(f'/api/v1/orders/{project_a_id}?page_size=10', headers=headers)
        assert r.status_code == 200

        r = await client.get(f'/api/v1/order-management/{project_a_id}/orders/stats', headers=headers)
        assert r.status_code == 200

@pytest.mark.asyncio
async def test_get_message_same_tenant():
    from app.domains.messages.service import MessageService
    from app.core.uow import UnitOfWork
    user_id = uuid4()
    project_id = uuid4()
    message_id = uuid4()
    async with AsyncSessionLocal() as db:
        user = User(id=user_id, email=f"test_{user_id}@example.com", password_hash="hash", role="admin")
        db.add(user)
        project = Project(id=project_id, owner_id=user_id, project_code=f"PRJ_{project_id}", name="Test Project", timezone="UTC")
        db.add(project)
        msg = Message(id=message_id, project_id=project_id, direction=MessageDirection.INBOUND, platform="test", provider="test", status="queued", content="hello")
        db.add(msg)
        await db.commit()

    async with AsyncSessionLocal() as db:
        uow = UnitOfWork(db)
        svc = MessageService(uow)
        context = TenantContext(user_id=user_id, project_id=project_id, role="admin")
        fetched = await svc.get_message(context, message_id)
        assert fetched.id == message_id

@pytest.mark.asyncio
async def test_get_message_cross_tenant():
    from app.domains.messages.service import MessageService
    from app.core.uow import UnitOfWork
    user_id = uuid4()
    project_id = uuid4()
    project_b_id = uuid4()
    message_id = uuid4()
    async with AsyncSessionLocal() as db:
        user = User(id=user_id, email=f"test_{user_id}@example.com", password_hash="hash", role="admin")
        db.add(user)
        project = Project(id=project_id, owner_id=user_id, project_code=f"PRJ_{project_id}", name="Test Project", timezone="UTC")
        db.add(project)
        project_b = Project(id=project_b_id, owner_id=user_id, project_code=f"PRJ_{project_b_id}", name="Project B", timezone="UTC")
        db.add(project_b)
        msg = Message(id=message_id, project_id=project_b_id, direction=MessageDirection.INBOUND, platform="test", provider="test", status="queued", content="hello")
        db.add(msg)
        await db.commit()

    async with AsyncSessionLocal() as db:
        uow = UnitOfWork(db)
        svc = MessageService(uow)
        context = TenantContext(user_id=user_id, project_id=project_id, role="admin")

        with pytest.raises(HTTPException) as exc:
            await svc.get_message(context, message_id)
        assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_get_message_forged_project_id():
    from app.domains.messages.service import MessageService
    from app.core.uow import UnitOfWork
    user_id = uuid4()
    project_id = uuid4()
    project_b_id = uuid4()
    message_id = uuid4()
    async with AsyncSessionLocal() as db:
        user = User(id=user_id, email=f"test_{user_id}@example.com", password_hash="hash", role="admin")
        db.add(user)
        project = Project(id=project_id, owner_id=user_id, project_code=f"PRJ_{project_id}", name="Test Project", timezone="UTC")
        db.add(project)
        project_b = Project(id=project_b_id, owner_id=user_id, project_code=f"PRJ_{project_b_id}", name="Project B", timezone="UTC")
        db.add(project_b)
        msg = Message(id=message_id, project_id=project_b_id, direction=MessageDirection.INBOUND, platform="test", provider="test", status="queued", content="hello")
        db.add(msg)
        await db.commit()

    async with AsyncSessionLocal() as db:
        uow = UnitOfWork(db)
        svc = MessageService(uow)
        # Even if the caller somehow supplied project_b_id in raw input, the context is strictly project_id
        context = TenantContext(user_id=user_id, project_id=project_id, role="admin")

        with pytest.raises(HTTPException) as exc:
            await svc.get_message(context, message_id)
        assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_mark_message_read_mutation_isolation():
    from app.domains.messages.service import MessageService
    from app.core.uow import UnitOfWork
    user_id = uuid4()
    project_id = uuid4()
    project_b_id = uuid4()
    message_id = uuid4()
    async with AsyncSessionLocal() as db:
        user = User(id=user_id, email=f"test_{user_id}@example.com", password_hash="hash", role="admin")
        db.add(user)
        project = Project(id=project_id, owner_id=user_id, project_code=f"PRJ_{project_id}", name="Test Project", timezone="UTC")
        db.add(project)
        project_b = Project(id=project_b_id, owner_id=user_id, project_code=f"PRJ_{project_b_id}", name="Project B", timezone="UTC")
        db.add(project_b)
        msg = Message(id=message_id, project_id=project_b_id, direction=MessageDirection.INBOUND, platform="test", provider="test", status="queued", content="hello", is_read=False)
        db.add(msg)
        await db.commit()

    async with AsyncSessionLocal() as db:
        uow = UnitOfWork(db)
        svc = MessageService(uow)
        context = TenantContext(user_id=user_id, project_id=project_id, role="admin")

        with pytest.raises(HTTPException) as exc:
            await svc.mark_message_read(context, message_id)
        assert exc.value.status_code == 404

    # Verify message was NOT modified
    async with AsyncSessionLocal() as db:
        stmt = select(Message).where(Message.id == message_id)
        result = await db.execute(stmt)
        msg = result.scalar_one()
        assert msg.is_read is False

@pytest.mark.asyncio
async def test_mark_message_read_missing_context():
    from app.domains.messages.service import MessageService
    from app.core.uow import UnitOfWork
    async with AsyncSessionLocal() as db:
        uow = UnitOfWork(db)
        svc = MessageService(uow)
        # Should raise an error because context is invalid / None, simulating the dependency failing closed
        with pytest.raises(AttributeError):
            await svc.mark_message_read(None, uuid4())
