import hmac
import hashlib
import json
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from unittest.mock import patch

pytestmark = pytest.mark.asyncio

async def test_meta_webhook_challenge_success():
    """Verify Meta hub.challenge verification passes with correct token."""
    test_token = "valid_verify_token_123"
    with patch.object(settings, "WHATSAPP_VERIFY_TOKEN", test_token):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/api/v1/webhooks/inbound",
                params={
                    "hub.mode": "subscribe",
                    "hub.verify_token": test_token,
                    "hub.challenge": "CHALLENGE_ACCEPTED_987",
                }
            )
            assert response.status_code == 200
            assert response.text == "CHALLENGE_ACCEPTED_987"

async def test_meta_webhook_challenge_wrong_token():
    """Verify Meta challenge fails with 403 on invalid verify token."""
    with patch.object(settings, "WHATSAPP_VERIFY_TOKEN", "secret_token"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/api/v1/webhooks/inbound",
                params={
                    "hub.mode": "subscribe",
                    "hub.verify_token": "wrong_token",
                    "hub.challenge": "CHALLENGE_XYZ",
                }
            )
            assert response.status_code == 403
            assert response.json()["detail"] == "Verification failed"

async def test_meta_webhook_challenge_missing_token():
    """Verify Meta challenge fails with 403 when verify token is omitted."""
    with patch.object(settings, "WHATSAPP_VERIFY_TOKEN", "secret_token"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/api/v1/webhooks/inbound",
                params={"hub.mode": "subscribe", "hub.challenge": "CHALLENGE_XYZ"}
            )
            assert response.status_code == 403

async def test_meta_signature_verification_valid_and_invalid():
    """Test Meta signature verification: valid HMAC accepts, invalid HMAC rejects."""
    app_secret = "meta_test_secret_key"
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "biz_123",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"phone_number_id": "phone_999"},
                    "messages": [{"id": "m_1", "from": "12345", "timestamp": "1690000000", "type": "text", "text": {"body": "Hi"}}]
                }
            }]
        }]
    }
    body_bytes = json.dumps(payload).encode("utf-8")
    valid_sig = "sha256=" + hmac.new(app_secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
    invalid_sig = "sha256=0000000000000000000000000000000000000000000000000000000000000000"

    with patch.object(settings, "FACEBOOK_APP_SECRET", app_secret):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Invalid signature -> 403 Forbidden
            res_invalid = await client.post(
                "/api/v1/webhooks/inbound",
                content=body_bytes,
                headers={"Content-Type": "application/json", "X-Hub-Signature-256": invalid_sig}
            )
            assert res_invalid.status_code == 403
            assert res_invalid.json()["detail"] == "Invalid signature"

            # 2. Valid signature -> Accepted by gateway
            res_valid = await client.post(
                "/api/v1/webhooks/inbound",
                content=body_bytes,
                headers={"Content-Type": "application/json", "X-Hub-Signature-256": valid_sig}
            )
            assert res_valid.status_code == 200
            # Since phone_999 has no registered integration in test db, returns project_not_found safely
            assert res_valid.json()["status"] == "ignored"
            assert res_valid.json()["reason"] == "project_not_found"

async def test_discord_ping_pong_response():
    """Verify Discord PING event (type: 1) immediately returns PONG without error."""
    with patch("app.services.webhook_adapters.DiscordAdapter.verify_signature", return_value=True):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/webhooks/inbound",
                json={"type": 1},
                headers={"X-Signature-Ed25519": "dummy_sig"}
            )
            assert response.status_code == 200
            assert response.json() == {"type": 1}

async def test_unknown_platform_gracefully_ignored():
    """Verify completely unidentifiable webhook payloads return 200 ignored to prevent retry storms."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/webhooks/inbound",
            json={"random_custom_event": "foobar"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ignored"
        assert data.get("reason") == "unknown_platform"
