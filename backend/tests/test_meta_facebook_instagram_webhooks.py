"""
Comprehensive tests for Facebook and Instagram webhooks:
- GET challenge verification (centralized & legacy endpoints).
- HMAC-SHA256 signature verification (valid, invalid, missing).
- Event normalization (direct messages, comments, echo rejection).
- Tenant resolution via Integration page_id binding and isolation.
"""
import hmac
import hashlib
import json
import pytest
from uuid import uuid4
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

from app.main import app
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.domains.auth.models import User
from app.domains.projects.models import Project
from app.domains.integrations.models import Integration, IntegrationStatus, IntegrationProvider

pytestmark = pytest.mark.asyncio


def _sign(secret: str, body: bytes) -> str:
    """Generate Meta X-Hub-Signature-256 header."""
    return "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


async def test_meta_webhook_challenge_verification_all_endpoints():
    """Verify hub.challenge handling across inbound, facebook, and instagram routes."""
    token = "meta_verify_secret_token"
    pid = uuid4()
    with patch.object(settings, "WHATSAPP_VERIFY_TOKEN", token), \
         patch.object(settings, "META_VERIFY_TOKEN", token):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Centralized /api/v1/webhooks/inbound
            r1 = await client.get("/api/v1/webhooks/inbound", params={
                "hub.mode": "subscribe", "hub.verify_token": token, "hub.challenge": "CHALLENGE_INBOUND"
            })
            assert r1.status_code == 200
            assert r1.text == "CHALLENGE_INBOUND"

            # 2. Legacy Facebook /api/v1/webhooks/facebook/{project_id}
            r2 = await client.get(f"/api/v1/webhooks/facebook/{pid}", params={
                "hub.mode": "subscribe", "hub.verify_token": token, "hub.challenge": "CHALLENGE_FB"
            })
            assert r2.status_code == 200
            assert r2.text == "CHALLENGE_FB"

            # 3. Legacy Instagram /api/v1/webhooks/instagram/{project_id}
            r3 = await client.get(f"/api/v1/webhooks/instagram/{pid}", params={
                "hub.mode": "subscribe", "hub.verify_token": token, "hub.challenge": "CHALLENGE_IG"
            })
            assert r3.status_code == 200
            assert r3.text == "CHALLENGE_IG"

            # 4. Invalid token rejection (403)
            r_bad = await client.get("/api/v1/webhooks/inbound", params={
                "hub.mode": "subscribe", "hub.verify_token": "wrong_token", "hub.challenge": "FAIL"
            })
            assert r_bad.status_code == 403


async def test_meta_signature_verification_facebook_and_instagram():
    """Verify HMAC signature checks for Facebook and Instagram webhooks."""
    secret = "meta_app_secret_9988"
    fb_payload = {
        "object": "page",
        "entry": [{"id": "page_123", "messaging": [{"sender": {"id": "user_1"}, "message": {"mid": "m_1", "text": "Hello"}}]}]
    }
    body = json.dumps(fb_payload).encode("utf-8")
    valid_header = _sign(secret, body)
    invalid_header = "sha256=badbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadb"

    with patch.object(settings, "FACEBOOK_APP_SECRET", secret):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Missing signature -> 403
            res_missing = await client.post("/api/v1/webhooks/inbound", content=body, headers={"Content-Type": "application/json"})
            assert res_missing.status_code == 403

            # Invalid signature -> 403
            res_inv = await client.post("/api/v1/webhooks/inbound", content=body, headers={"Content-Type": "application/json", "X-Hub-Signature-256": invalid_header})
            assert res_inv.status_code == 403

            # Valid signature -> accepted by gateway
            res_val = await client.post("/api/v1/webhooks/inbound", content=body, headers={"Content-Type": "application/json", "X-Hub-Signature-256": valid_header})
            assert res_val.status_code == 200


async def test_facebook_and_instagram_echo_rejection():
    """Verify echo messages (outbound from bot) are ignored to prevent loops."""
    fb_echo = {
        "object": "page",
        "entry": [{"id": "page_echo", "messaging": [{"sender": {"id": "page_echo"}, "message": {"mid": "m_echo", "text": "Echo", "is_echo": True}}]}]
    }
    ig_echo = {
        "object": "instagram",
        "entry": [{"id": "ig_echo", "messaging": [{"sender": {"id": "ig_echo"}, "message": {"mid": "m_ig_echo", "text": "Echo", "is_echo": True}}]}]
    }

    with patch("app.services.webhook_adapters.MetaAdapter.verify_signature", return_value=True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r_fb = await client.post("/api/v1/webhooks/inbound", json=fb_echo)
            assert r_fb.status_code == 200
            assert r_fb.json()["status"] == "ignored"

            r_ig = await client.post("/api/v1/webhooks/inbound", json=ig_echo)
            assert r_ig.status_code == 200
            assert r_ig.json()["status"] == "ignored"


async def test_facebook_and_instagram_tenant_routing_and_isolation():
    """Verify Facebook and Instagram webhooks route to correct tenant via page_id."""
    async with AsyncSessionLocal() as session:
        user = User(id=uuid4(), email=f"meta_test_{uuid4().hex[:8]}@example.com", password_hash="pw", is_active=True)
        session.add(user)

        # Tenant A with Facebook
        project_a = Project(id=uuid4(), owner_id=user.id, name="Brand A", project_code=f"PRJ-FB-{uuid4().hex[:6]}")
        session.add(project_a)
        fb_page_id = f"fb_page_{uuid4().hex[:8]}"
        int_fb = Integration(
            project_id=project_a.id,
            provider="facebook",
            status=IntegrationStatus.CONNECTED,
            config={"page_id": fb_page_id, "access_token": "token_fb"},
        )
        session.add(int_fb)

        # Tenant B with Instagram
        project_b = Project(id=uuid4(), owner_id=user.id, name="Brand B", project_code=f"PRJ-IG-{uuid4().hex[:6]}")
        session.add(project_b)
        ig_page_id = f"ig_page_{uuid4().hex[:8]}"
        int_ig = Integration(
            project_id=project_b.id,
            provider="instagram",
            status=IntegrationStatus.CONNECTED,
            config={"page_id": ig_page_id, "access_token": "token_ig"},
        )
        session.add(int_ig)
        await session.commit()

        # Send Facebook webhook -> maps to Tenant A
        fb_payload = {
            "object": "page",
            "entry": [{"id": fb_page_id, "messaging": [{"sender": {"id": "c_1"}, "message": {"mid": "mid_fb_1", "text": "What is the price?"}}]}]
        }

        # Send Instagram webhook -> maps to Tenant B
        ig_payload = {
            "object": "instagram",
            "entry": [{"id": ig_page_id, "messaging": [{"sender": {"id": "c_2"}, "message": {"mid": "mid_ig_1", "text": "Do you ship abroad?"}}]}]
        }

        with patch("app.services.webhook_adapters.MetaAdapter.verify_signature", return_value=True), \
             patch("app.services.webhook_processor.WebhookProcessor.process_message") as mock_proc:
            mock_proc.return_value = None
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                res_fb = await client.post("/api/v1/webhooks/inbound", json=fb_payload)
                assert res_fb.status_code == 200
                assert res_fb.json()["status"] == "processed"
                assert res_fb.json()["project_id"] == str(project_a.id)

                res_ig = await client.post("/api/v1/webhooks/inbound", json=ig_payload)
                assert res_ig.status_code == 200
                assert res_ig.json()["status"] == "processed"
                assert res_ig.json()["project_id"] == str(project_b.id)

                # Unregistered page_id -> ignored with project_not_found (no leakage)
                unmapped_payload = {
                    "object": "page",
                    "entry": [{"id": "unknown_page_999", "messaging": [{"sender": {"id": "c_x"}, "message": {"mid": "mid_x", "text": "Spam"}}]}]
                }
                res_unmapped = await client.post("/api/v1/webhooks/inbound", json=unmapped_payload)
                assert res_unmapped.status_code == 200
                assert res_unmapped.json()["status"] == "ignored"
                assert res_unmapped.json()["reason"] == "project_not_found"
