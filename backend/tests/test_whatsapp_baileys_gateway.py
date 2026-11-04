"""
Unit and integration tests for WhatsApp Baileys Gateway provider in Automind.
"""

import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.integrations.whatsapp_baileys import WhatsAppBaileysService
from app.services.whatsapp_gateway_client import WhatsAppGatewayClient
from app.services.webhook_adapters import WAGatewayAdapter
from app.api.v1.whatsapp_session_helpers import _sanitize_session_response


def test_baileys_service_normalization_text():
    """Verify inbound Baileys text payload normalization."""
    service = WhatsAppBaileysService(session_id="test-session")
    raw_payload = {
        "session_id": "test-session",
        "message": {
            "key": {
                "id": "BAILEYS_MSG_001",
                "remoteJid": "201001234567@s.whatsapp.net",
                "fromMe": False
            },
            "messageTimestamp": 1730000000,
            "pushName": "Ahmed Customer",
            "message": {
                "conversation": "Hello, I want to inquire about products."
            }
        },
        "metadata": {"project_id": "proj-uuid-123"}
    }

    normalized = service.parse_webhook(raw_payload)
    assert normalized is not None
    assert normalized["message_id"] == "BAILEYS_MSG_001"
    assert normalized["from"] == "201001234567"
    assert normalized["text"] == "Hello, I want to inquire about products."
    assert normalized["contact"]["name"] == "Ahmed Customer"
    assert normalized["from_me"] is False
    assert normalized["session_id"] == "test-session"
    assert normalized["project_id"] == "proj-uuid-123"


def test_baileys_service_normalization_media():
    """Verify inbound Baileys media payload extraction."""
    service = WhatsAppBaileysService(session_id="test-session")
    raw_payload = {
        "session_id": "test-session",
        "message": {
            "key": {
                "id": "BAILEYS_MEDIA_002",
                "remoteJid": "201001234567@s.whatsapp.net",
                "fromMe": False
            },
            "messageTimestamp": 1730000050,
            "pushName": "Client Media",
            "message": {
                "imageMessage": {
                    "url": "https://storage.whatsapp.net/media_img_123.jpg",
                    "mimetype": "image/jpeg",
                    "caption": "Order receipt attachment",
                    "fileLength": 1048576
                }
            }
        }
    }

    normalized = service.parse_webhook(raw_payload)
    assert normalized is not None
    assert normalized["media_type"] == "image"
    assert normalized["text"] == "Order receipt attachment"
    assert normalized["media_data"]["mimetype"] == "image/jpeg"
    assert normalized["media_data"]["file_length"] == 1048576


def test_wa_gateway_adapter_normalize():
    """Verify WAGatewayAdapter converts Baileys payload into Automind WebhookEvent."""
    adapter = WAGatewayAdapter()
    payload = {
        "session_id": "sess-xyz",
        "message": {
            "key": {
                "id": "EVENT_099",
                "remoteJid": "15551234567@s.whatsapp.net",
                "fromMe": False
            },
            "messageTimestamp": 1730000100,
            "pushName": "Sarah",
            "message": {
                "conversation": "What are your delivery hours?"
            }
        }
    }

    event = adapter.normalize(payload)
    assert event is not None
    assert event.event_id == "EVENT_099"
    assert event.platform == "wa_gateway"
    assert event.channel == "whatsapp"
    assert event.sender_id == "15551234567"
    assert event.sender_name == "Sarah"
    assert event.payload["text"] == "What are your delivery hours?"
    assert event.payload["session_id"] == "sess-xyz"


def test_secret_redaction_and_sanitization():
    """Verify internal API keys and secrets are never leaked."""
    client = WhatsAppGatewayClient(base_url="http://gw.internal:3000", api_key="secret-api-key-999")
    sensitive_err = "Request failed with Bearer secret-api-key-999 and password=abc"
    clean_msg = client._sanitize_message(sensitive_err)

    assert "secret-api-key-999" not in clean_msg
    assert "[REDACTED]" in clean_msg

    raw_response = {
        "status": "connected",
        "session_id": "sess-123",
        "api_key": "raw-key-must-not-leak",
        "access_token": "token-123",
        "metadata": {
            "secret": "db-secret",
            "project_id": "11111111-1111-1111-1111-111111111111"
        }
    }
    safe_response = _sanitize_session_response(raw_response)
    assert "api_key" not in safe_response
    assert "access_token" not in safe_response
    assert "secret" not in safe_response["metadata"]
    assert safe_response["metadata"]["project_id"] == "11111111-1111-1111-1111-111111111111"


def test_jid_normalization():
    """Verify phone numbers are safely converted to standard WhatsApp JIDs."""
    assert WhatsAppBaileysService.normalize_jid("+1 (555) 019-2834") == "1 (555) 019-2834@s.whatsapp.net"
    assert WhatsAppBaileysService.normalize_jid("201012345678@s.whatsapp.net") == "201012345678@s.whatsapp.net"
    assert WhatsAppBaileysService.normalize_jid("201012345678@c.us") == "201012345678@s.whatsapp.net"
    assert WhatsAppBaileysService.normalize_jid("") == ""
