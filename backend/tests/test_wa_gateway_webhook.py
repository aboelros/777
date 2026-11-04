from uuid import UUID
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.core.config import settings
import time
import hmac
import hashlib

client = TestClient(app)

def make_signature(secret: str, timestamp: str, body: bytes) -> str:
    payload_to_sign = f"{timestamp}.".encode("utf-8") + body
    return hmac.new(secret.encode(), payload_to_sign, hashlib.sha256).hexdigest()

@pytest.fixture
def mock_gateway():
    with patch("app.services.webhook_gateway.WebhookGateway._dispatch") as mock_dispatch, \
         patch("app.services.webhook_resolver.WebhookProjectResolver.resolve_project", return_value="test_project") as mock_resolve:
        yield mock_dispatch

@pytest.fixture
def setup_secret():
    old_secret = settings.WA_GATEWAY_API_KEY
    settings.WA_GATEWAY_API_KEY = "test_integration_secret"
    yield "test_integration_secret"
    settings.WA_GATEWAY_API_KEY = old_secret

def test_webhook_valid_payload(mock_gateway, setup_secret):
    body = b'{"session_id": "test_session", "text": "hello", "from": "12345"}'
    timestamp = str(int(time.time()))
    sig = make_signature(setup_secret, timestamp, body)
    
    response = client.post(
        "/api/v1/webhooks/inbound",
        content=body,
        headers={
            "X-WA-Signature": sig,
            "X-WA-Timestamp": timestamp,
            "Content-Type": "application/json"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"status": "processed", "project_id": "test_project"}
    mock_gateway.assert_called_once()

def test_webhook_invalid_signature(mock_gateway, setup_secret):
    body = b'{"session_id": "test_session", "text": "hello", "from": "12345"}'
    timestamp = str(int(time.time()))
    
    response = client.post(
        "/api/v1/webhooks/inbound",
        content=body,
        headers={
            "X-WA-Signature": "bad_signature_hex",
            "X-WA-Timestamp": timestamp,
            "Content-Type": "application/json"
        }
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid signature"}
    mock_gateway.assert_not_called()

def test_webhook_missing_signature(mock_gateway, setup_secret):
    body = b'{"session_id": "test_session", "text": "hello", "from": "12345"}'
    timestamp = str(int(time.time()))
    
    response = client.post(
        "/api/v1/webhooks/inbound",
        content=body,
        headers={
            "X-WA-Timestamp": timestamp,
            "Content-Type": "application/json"
        }
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid signature"}
    mock_gateway.assert_not_called()

def test_webhook_stale_timestamp(mock_gateway, setup_secret):
    body = b'{"session_id": "test_session", "text": "hello", "from": "12345"}'
    stale_timestamp = str(int(time.time()) - 400) # 400 seconds ago (limit is 300)
    sig = make_signature(setup_secret, stale_timestamp, body)
    
    response = client.post(
        "/api/v1/webhooks/inbound",
        content=body,
        headers={
            "X-WA-Signature": sig,
            "X-WA-Timestamp": stale_timestamp,
            "Content-Type": "application/json"
        }
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid signature"}
    mock_gateway.assert_not_called()

def test_webhook_modified_body(mock_gateway, setup_secret):
    body = b'{"session_id": "test_session", "text": "hello", "from": "12345"}'
    timestamp = str(int(time.time()))
    sig = make_signature(setup_secret, timestamp, body)
    
    # Tamper with the body
    tampered_body = b'{"session_id": "test_session", "text": "tampered", "from": "12345"}'
    
    response = client.post(
        "/api/v1/webhooks/inbound",
        content=tampered_body,
        headers={
            "X-WA-Signature": sig,
            "X-WA-Timestamp": timestamp,
            "Content-Type": "application/json"
        }
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid signature"}
    mock_gateway.assert_not_called()

def test_webhook_modified_timestamp(mock_gateway, setup_secret):
    body = b'{"session_id": "test_session", "text": "hello", "from": "12345"}'
    timestamp = str(int(time.time()))
    sig = make_signature(setup_secret, timestamp, body)
    
    tampered_timestamp = str(int(time.time()) + 10)
    
    response = client.post(
        "/api/v1/webhooks/inbound",
        content=body,
        headers={
            "X-WA-Signature": sig,
            "X-WA-Timestamp": tampered_timestamp,
            "Content-Type": "application/json"
        }
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid signature"}
    mock_gateway.assert_not_called()

def test_webhook_wrong_secret(mock_gateway, setup_secret):
    body = b'{"session_id": "test_session", "text": "hello", "from": "12345"}'
    timestamp = str(int(time.time()))
    sig = make_signature("wrong_secret", timestamp, body)
    
    response = client.post(
        "/api/v1/webhooks/inbound",
        content=body,
        headers={
            "X-WA-Signature": sig,
            "X-WA-Timestamp": timestamp,
            "Content-Type": "application/json"
        }
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid signature"}
    mock_gateway.assert_not_called()
