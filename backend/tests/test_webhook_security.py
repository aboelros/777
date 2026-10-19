from unittest.mock import patch
import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.models import Project, CustomerProfile, Message, User
from app.domains.integrations.models import Integration, IntegrationStatus, IntegrationProvider
from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal

pytestmark = pytest.mark.asyncio

async def setup_projects(db):
    user_email = f"test_{uuid.uuid4()}@example.com"
    user = User(id=uuid.uuid4(), email=user_email, password_hash="pw", is_active=True)
    db.add(user)
    await db.commit()
    
    project_a = Project(id=uuid.uuid4(), owner_id=user.id, name="Project A", project_code=str(uuid.uuid4())[:8])
    db.add(project_a)
    project_b = Project(id=uuid.uuid4(), owner_id=user.id, name="Project B", project_code=str(uuid.uuid4())[:8])
    db.add(project_b)
    await db.commit()
    return project_a, project_b, user_email

async def teardown_projects(db, email, project_ids=None):
    if project_ids:
        await db.execute(delete(Integration).where(Integration.project_id.in_(project_ids)))
        await db.execute(delete(Project).where(Project.id.in_(project_ids)))
    await db.execute(delete(User).where(User.email == email))
    await db.commit()

async def test_a_arbitrary_fallback_blocked():
    async with AsyncSessionLocal() as db:
        project_a, project_b, email = await setup_projects(db)
        
        integration_a = Integration(
            project_id=project_a.id,
            provider=IntegrationProvider.TELEGRAM,
            status=IntegrationStatus.CONNECTED,
            config={"api_key": "test_token"}
        )
        db.add(integration_a)
        
        integration_b = Integration(
            project_id=project_b.id,
            provider=IntegrationProvider.TELEGRAM,
            status=IntegrationStatus.CONNECTED,
            config={"api_key": "test_token_b"}
        )
        db.add(integration_b)
        await db.commit()
        
        payload = {
            "update_id": 12345,
            "message": {
                "message_id": 1,
                "from": {"id": 999, "is_bot": False, "first_name": "Attacker"},
                "chat": {"id": 999, "type": "private"},
                "date": 1690000000,
                "text": "Hello"
            }
        }
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/webhooks/inbound",
                json=payload,
                headers={"X-Telegram-Bot-Api-Secret-Token": "test_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "ignored"
            assert data.get("reason") == "project_not_found"
            assert "project_id" not in data
            
        # Prove no side effects for these projects
        profiles = await db.execute(select(CustomerProfile).where(CustomerProfile.project_id.in_([project_a.id, project_b.id])))
        assert len(profiles.scalars().all()) == 0
        messages = await db.execute(select(Message).where(Message.project_id.in_([project_a.id, project_b.id])))
        assert len(messages.scalars().all()) == 0
            
        await teardown_projects(db, email, [project_a.id, project_b.id])

@patch("app.services.webhook_adapters.WAGatewayAdapter.verify_signature", return_value=True)
async def test_b_valid_deterministic_routing(mock_sig):
    async with AsyncSessionLocal() as db:
        project_a, project_b, email = await setup_projects(db)
        
        integration_b = Integration(
            project_id=project_b.id,
            provider=IntegrationProvider.WHATSAPP,
            status=IntegrationStatus.CONNECTED,
            extra_data={"provider": "wa_gateway", "session_id": "secure_session_123"}
        )
        db.add(integration_b)
        await db.commit()
        
        payload = {
            "data": {
                "session_id": "secure_session_123",
                "id": "msg_123",
                "from": "1234567890",
                "pushName": "Valid User",
                "messageType": "conversation",
                "text": "Hello valid"
            }
        }
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/webhooks/inbound",
                json=payload
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "processed"
            assert data.get("project_id") == str(project_b.id)
            
        await teardown_projects(db, email, [project_a.id, project_b.id])

@patch("app.services.webhook_adapters.WAGatewayAdapter.verify_signature", return_value=True)
async def test_c_ambiguous_routing_rejected(mock_sig):
    async with AsyncSessionLocal() as db:
        project_a, project_b, email = await setup_projects(db)
        
        integration_a = Integration(
            project_id=project_a.id,
            provider=IntegrationProvider.WHATSAPP,
            status=IntegrationStatus.CONNECTED,
            extra_data={"provider": "wa_gateway", "session_id": "ambiguous_session"}
        )
        integration_b = Integration(
            project_id=project_b.id,
            provider=IntegrationProvider.WHATSAPP,
            status=IntegrationStatus.CONNECTED,
            extra_data={"provider": "wa_gateway", "session_id": "ambiguous_session"}
        )
        db.add(integration_a)
        db.add(integration_b)
        await db.commit()
        
        payload = {
            "data": {
                "session_id": "ambiguous_session",
                "id": "msg_456",
                "from": "0987654321",
                "pushName": "Ambiguous User",
                "messageType": "conversation",
                "text": "Hello ambiguous"
            }
        }
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/webhooks/inbound",
                json=payload
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "ignored"
            assert data.get("reason") == "project_not_found"
            
        # Prove no side effects for these projects
        profiles = await db.execute(select(CustomerProfile).where(CustomerProfile.project_id.in_([project_a.id, project_b.id])))
        assert len(profiles.scalars().all()) == 0
        messages = await db.execute(select(Message).where(Message.project_id.in_([project_a.id, project_b.id])))
        assert len(messages.scalars().all()) == 0
            
        await teardown_projects(db, email, [project_a.id, project_b.id])

async def test_d_legacy_routes_deleted():
    test_project_id = uuid.uuid4()
    routes = [
        f"/api/v1/chat-bot/{test_project_id}/webhook/whatsapp",
        f"/api/v1/chat-bot/{test_project_id}/webhook/telegram",
        f"/api/v1/chat-bot/{test_project_id}/webhook/discord",
        f"/api/v1/chat-bot/{test_project_id}/webhook/tiktok"
    ]
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for route in routes:
            res = await client.post(route, json={})
            assert res.status_code == 404, f"Route {route} still exists!"
