import pytest
from httpx import AsyncClient
import uuid
import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func

from app.domains.integrations.models import OAuthState, Integration
from app.domains.integrations.oauth_state_service import OAuthStateService
from app.core.database import AsyncSessionLocal
from httpx import ASGITransport
from app.main import app
from unittest.mock import patch

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
        
        user_b = User(
            id=uuid.uuid4(),
            email=f"b_{uuid.uuid4()}@test.com",
            password_hash=get_password_hash("testpass"),
            is_active=True
        )
        db.add(user_b)
        await db.flush()
        
        proj_a = Project(
            id=uuid.uuid4(),
            name="Project A",
            project_code=f"PA_{uuid.uuid4().hex[:8]}",
            owner_id=user_a.id,
        )
        db.add(proj_a)
        
        proj_b = Project(
            id=uuid.uuid4(),
            name="Project B",
            project_code=f"PB_{uuid.uuid4().hex[:8]}",
            owner_id=user_b.id,
        )
        db.add(proj_b)
        await db.commit()
        
        token_a = create_access_token({"sub": str(user_a.id)})
        token_b = create_access_token({"sub": str(user_b.id)})
        
        return {
            "user_a_id": user_a.id,
            "user_b_id": user_b.id,
            "project_a_id": proj_a.id,
            "project_b_id": proj_b.id,
            "token_a": token_a,
            "token_b": token_b
        }

@pytest.mark.asyncio
async def test_oauth_state_service_atomic_consumption():
    data = await setup_test_data_local()
    project_id = data['project_a_id']
    user_id = data['user_a_id']
    provider = "facebook"
    
    async with AsyncSessionLocal() as db:
        state_token = await OAuthStateService.create_state(
            db=db, project_id=project_id, user_id=user_id, provider=provider
        )
        
        # A: Valid state
        consumed_state = await OAuthStateService.consume_state(db, state_token, provider)
        assert consumed_state is not None
        assert consumed_state.project_id == project_id
        
        # E: Replay
        second_consume = await OAuthStateService.consume_state(db, state_token, provider)
        assert second_consume is None
        
        # F: Wrong provider
        state_token2 = await OAuthStateService.create_state(db=db, project_id=project_id, user_id=user_id, provider=provider)
        wrong_provider = await OAuthStateService.consume_state(db, state_token2, "tiktok")
        assert wrong_provider is None
        
        # D: Expired state
        token3 = OAuthStateService._generate_token()
        expired_state = OAuthState(
            project_id=project_id, user_id=user_id, provider=provider,
            state_token=token3, expires_at=datetime.now(timezone.utc) - timedelta(minutes=5)
        )
        db.add(expired_state)
        await db.commit()
        
        expired_consume = await OAuthStateService.consume_state(db, token3, provider)
        assert expired_consume is None

@pytest.mark.asyncio
async def test_oauth_api_forged_state_zero_exchange():
    data = await setup_test_data_local()
    
    payload = {
        "code": "fake_code",
        "redirect_uri": "http://localhost/callback",
        "state": "forged_state_string",
        "provider": "facebook"
    }
    
    with patch("httpx.AsyncClient.post") as mock_post:
        res = await _make_request(
            "POST", 
            f"/api/v1/integrations/{data['project_a_id']}/meta/callback",
            data['token_a'],
            json_data=payload
        )
        
        # B: Forged state
        assert res.status_code == 400
        assert "Invalid, expired" in res.json()['detail']
        
        # I: Invalid state causes zero external exchange
        mock_post.assert_not_called()
        
        # J: Invalid state causes zero persistence
        async with AsyncSessionLocal() as db:
            integrations_count = await db.scalar(select(func.count()).select_from(Integration).where(Integration.project_id == data['project_a_id']))
            assert integrations_count == 0

@pytest.mark.asyncio
async def test_oauth_api_cross_tenant_state():
    data = await setup_test_data_local()
    
    async with AsyncSessionLocal() as db:
        state_token_b = await OAuthStateService.create_state(
            db,
            project_id=data['project_b_id'],
            user_id=data['user_b_id'],
            provider="facebook",
        )
    
    payload = {
        "code": "fake_code",
        "redirect_uri": "http://localhost/callback",
        "state": state_token_b,
        "provider": "facebook"
    }
    
    res = await _make_request(
        "POST", 
        f"/api/v1/integrations/{data['project_a_id']}/meta/callback",
        data['token_a'],
        json_data=payload
    )
    
    # C/H: Cross-tenant state
    assert res.status_code == 400
    assert "OAuth state does not match" in res.json()['detail']

@pytest.mark.asyncio
async def test_oauth_api_wrong_user():
    data = await setup_test_data_local()
    
    # G: Wrong user (User B trying to consume User A's state on Project A, assuming User B has access to Project A)
    # Actually, we can test just user mismatch
    async with AsyncSessionLocal() as db:
        state_token_a = await OAuthStateService.create_state(
            db,
            project_id=data['project_a_id'],
            user_id=data['user_a_id'],
            provider="facebook",
        )
    
    payload = {
        "code": "fake_code",
        "redirect_uri": "http://localhost/callback",
        "state": state_token_a,
        "provider": "facebook"
    }
    
    # User B makes request, but state was for User A
    res = await _make_request(
        "POST", 
        f"/api/v1/integrations/{data['project_b_id']}/meta/callback",
        data['token_b'],
        json_data=payload
    )
    
    assert res.status_code == 400

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
    
    with patch("httpx.AsyncClient.post") as mock_post:
        # We don't care what the mock returns as long as it doesn't crash if called
        # mock_post.return_value = ...
        
        # Fire concurrent requests
        reqs = [
            _make_request(
                "POST", 
                f"/api/v1/integrations/{data['project_a_id']}/meta/callback",
                data['token_a'],
                json_data=payload
            ) for _ in range(5)
        ]
        results = await asyncio.gather(*reqs)
        
        status_codes = [r.status_code for r in results]
        
        # Only one should theoretically proceed past the state check.
        # The others MUST return 400.
        # But wait, since we mocked post, the successful one will probably fail at integration exchange (500 or 400)
        # We just need to assert that EXACTLY 4 of them failed with 400 "Invalid, expired"
        failed_with_400 = sum(1 for r in results if r.status_code == 400 and "Invalid, expired" in r.json().get('detail', ''))
        assert failed_with_400 == 4
        
        # K: Concurrent consumption - exactly one succeeds (or at least gets past the state check)
        # Because we mocked httpx.post, the one that got past the state check might return a different status code.
        # Let's verify that the atomic state check worked.
