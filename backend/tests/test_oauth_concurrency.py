import pytest
from httpx import AsyncClient
import uuid
import asyncio
from datetime import datetime, timedelta, timezone

from app.domains.integrations.models import OAuthState, Integration
from app.domains.integrations.oauth_state_service import OAuthStateService
from app.core.database import AsyncSessionLocal
from httpx import ASGITransport
from app.main import app

async def _make_request(method, url, token, json_data=None):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        return await client.request(
            method, 
            url, 
            headers={"Authorization": f"Bearer {token}"},
            json=json_data
        )

# Mocked setup_test_data
async def setup_test_data_local():
    from app.domains.auth.models import User
    from app.domains.projects.models import Project
    from app.core.security import get_password_hash, create_access_token

    async with AsyncSessionLocal() as db:
        user_a = User(
            id=uuid.uuid4(),
            email=f"a_{uuid.uuid4()}@test.com",
            password_hash=get_password_hash("testpass"),
            is_active=True
        )
        db.add(user_a)
        await db.flush()
        
        proj_a = Project(
            id=uuid.uuid4(),
            name="Project A",
            project_code=f"PA_{uuid.uuid4().hex[:8]}",
            owner_id=user_a.id,
        )
        db.add(proj_a)
        await db.commit()
        
        token_a = create_access_token({"sub": str(user_a.id)})
        
        return {
            "user_a_id": user_a.id,
            "project_a_id": proj_a.id,
            "token_a": token_a,
        }

@pytest.mark.asyncio
async def test_oauth_api_concurrent_consumption():
    data = await setup_test_data_local()
    
    async with AsyncSessionLocal() as db:
        state_token = await OAuthStateService.create_state(
            db,
            project_id=data['project_a_id'],
            user_id=data['user_a_id'],
            provider="facebook",
        )
        
    payload = {
        "code": "fake_code",
        "redirect_uri": "http://localhost/callback",
        "state": state_token,
        "provider": "facebook"
    }
    
    reqs = [
        _make_request(
            "POST", 
            f"/api/v1/integrations/{data['project_a_id']}/meta/callback",
            data['token_a'],
            json_data=payload
        ) for _ in range(5)
    ]
    results = await asyncio.gather(*reqs)
    
    failed_with_state = 0
    succeeded_state = 0
    
    for r in results:
        print("STATUS", r.status_code, "RESPONSE", r.json())
        detail = r.json().get('detail', '')
        if "OAuth state" in detail:
            failed_with_state += 1
        elif "Meta authentication failed" in detail:
            succeeded_state += 1
            
    assert failed_with_state == 4
    assert succeeded_state == 1


@pytest.mark.asyncio
async def test_oauth_service_direct_bypass():
    data = await setup_test_data_local()
    
    async with AsyncSessionLocal() as db:
        # Create a state
        state_token = await OAuthStateService.create_state(
            db,
            project_id=data['project_a_id'],
            user_id=data['user_a_id'],
            provider="facebook",
        )
        
        # Test 1: Wrong provider
        state = await OAuthStateService.consume_state(db, state_token, "tiktok")
        assert state is None
        
        # Test 2: Consume it correctly
        state = await OAuthStateService.consume_state(db, state_token, "facebook")
        assert state is not None
        assert state.project_id == data['project_a_id']
        assert state.user_id == data['user_a_id']
        
        # Test 3: Replay (already consumed)
        state2 = await OAuthStateService.consume_state(db, state_token, "facebook")
        assert state2 is None

        # Test 4: Forged state
        state3 = await OAuthStateService.consume_state(db, "fake_state_123", "facebook")
        assert state3 is None
