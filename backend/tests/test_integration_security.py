import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select, delete
from app.main import app
from app.db.models import Project, User, ProjectMember, ProjectRole
from app.domains.integrations.models import Integration, IntegrationStatus
from app.core.database import AsyncSessionLocal
from app.core.security import create_access_token
import json

pytestmark = pytest.mark.asyncio

async def setup_test_data():
    async with AsyncSessionLocal() as db:
        user_a = User(id=uuid.uuid4(), email=f"a_{uuid.uuid4()}@ex.com", is_active=True, password_hash="hash")
        project_a = Project(id=uuid.uuid4(), name="Project A", owner_id=user_a.id, project_code=str(uuid.uuid4())[:8])
        
        user_b = User(id=uuid.uuid4(), email=f"b_{uuid.uuid4()}@ex.com", is_active=True, password_hash="hash")
        project_b = Project(id=uuid.uuid4(), name="Project B", owner_id=user_b.id, project_code=str(uuid.uuid4())[:8])
        
        user_c = User(id=uuid.uuid4(), email=f"c_{uuid.uuid4()}@ex.com", is_active=True, password_hash="hash")
        
        db.add_all([user_a, project_a, user_b, project_b, user_c])
        await db.commit()
        
        # Make User C a member of Project A
        member_c = ProjectMember(project_id=project_a.id, user_id=user_c.id, role=ProjectRole.MODERATOR)
        db.add(member_c)
        await db.commit()
        
        int_a = Integration(
            project_id=project_a.id,
            provider="whatsapp",
            status=IntegrationStatus.CONNECTED,
            config={"api_key": "secret_key_a", "phone_number": "123"}
        )
        int_b = Integration(
            project_id=project_b.id,
            provider="telegram",
            status=IntegrationStatus.CONNECTED,
            config={"bot_token": "secret_token_b"}
        )
        db.add_all([int_a, int_b])
        await db.commit()
        
        token_a = create_access_token({"sub": str(user_a.id)})
        token_b = create_access_token({"sub": str(user_b.id)})
        token_c = create_access_token({"sub": str(user_c.id)})
        
        return {
            "token_a": token_a,
            "project_a_id": str(project_a.id),
            "int_a_id": str(int_a.id),
            "token_b": token_b,
            "project_b_id": str(project_b.id),
            "int_b_id": str(int_b.id),
            "token_c": token_c
        }

async def _make_request(method, path, token, json_data=None):
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(app=app, base_url="http://test") as client:
        if method == "GET":
            return await client.get(path, headers=headers)
        elif method == "POST":
            return await client.post(path, headers=headers, json=json_data)
        elif method == "PATCH":
            return await client.patch(path, headers=headers, json=json_data)
        elif method == "DELETE":
            return await client.delete(path, headers=headers)

async def test_a_cross_tenant_read_blocked():
    data = await setup_test_data()
    res = await _make_request("GET", f"/api/v1/integrations/{data['project_a_id']}/{data['int_a_id']}", data["token_b"])
    assert res.status_code in [403, 404]

async def test_b_cross_tenant_update_blocked():
    data = await setup_test_data()
    res = await _make_request("PATCH", f"/api/v1/integrations/{data['project_a_id']}/{data['int_a_id']}", data["token_b"], json_data={"status": "disconnected"})
    assert res.status_code in [403, 404]

async def test_c_cross_tenant_delete_blocked():
    data = await setup_test_data()
    res = await _make_request("DELETE", f"/api/v1/integrations/{data['project_a_id']}/{data['int_a_id']}", data["token_b"])
    assert res.status_code in [403, 404]

async def test_d_cross_tenant_list_isolation():
    data = await setup_test_data()
    res_a = await _make_request("GET", f"/api/v1/integrations/{data['project_a_id']}", data["token_b"])
    assert res_a.status_code in [403, 404]

async def test_e_cross_tenant_side_effect_prevention(mocker):
    data = await setup_test_data()
    mock_sync = mocker.patch("app.workers.celery_app.celery_app.send_task")
    res = await _make_request("POST", f"/api/v1/integrations/{data['project_a_id']}/{data['int_a_id']}/sync", data["token_b"])
    assert res.status_code in [403, 404]
    mock_sync.assert_not_called()

async def test_f_same_tenant_functionality_preserved():
    data = await setup_test_data()
    res = await _make_request("GET", f"/api/v1/integrations/{data['project_a_id']}/{data['int_a_id']}", data["token_a"])
    assert res.status_code == 200

async def test_g_credential_masking():
    data = await setup_test_data()
    res = await _make_request("GET", f"/api/v1/integrations/{data['project_a_id']}/{data['int_a_id']}", data["token_a"])
    assert res.status_code == 200
    res_data = res.json()
    config = res_data.get("config", {})
    assert "api_key" in config
    assert "secret" not in config["api_key"]
    assert "***" in config["api_key"]
    assert config.get("phone_number") == "123"

async def test_h_same_project_different_user():
    data = await setup_test_data()
    res = await _make_request("GET", f"/api/v1/integrations/{data['project_a_id']}/{data['int_a_id']}", data["token_c"])
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["id"] == data["int_a_id"]
