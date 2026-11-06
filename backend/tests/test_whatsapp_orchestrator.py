"""
Tests for WhatsApp and multi-channel orchestrator client resolution.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4

from app.domains.customers.models import CustomerProfile
from app.domains.ai.models import ModelTraining
from app.domains.analytics.models import Report
from app.domains.integrations.models import Integration, IntegrationStatus
from app.services.integrations.whatsapp import WhatsAppService
from app.services.integrations.whatsapp_baileys import WhatsAppBaileysService
from app.services.integrations.telegram import TelegramService
from app.domains.ai.orchestrator import AIOrchestrator
from app.services.service_factory import get_whatsapp_gateway_service


def test_whatsapp_service_dict_and_positional_init():
    """Verify WhatsAppService safely handles both dict config and positional args."""
    # Dict initialization
    svc1 = WhatsAppService({"phone_number_id": "123456", "access_token": "token_abc"})
    assert svc1.business_id == "123456"
    assert svc1.access_token == "token_abc"

    # Positional initialization
    svc2 = WhatsAppService("987654", "token_xyz")
    assert svc2.business_id == "987654"
    assert svc2.access_token == "token_xyz"


def test_telegram_service_dict_and_positional_init():
    """Verify TelegramService safely handles both dict config and positional args."""
    svc1 = TelegramService({"bot_token": "bot12345:ABC"})
    assert svc1.bot_token == "bot12345:ABC"

    svc2 = TelegramService("bot99999:XYZ")
    assert svc2.bot_token == "bot99999:XYZ"


def test_baileys_normalize_jid_strips_formatting():
    """Verify normalize_jid strips out plus sign and appends domain."""
    assert WhatsAppBaileysService.normalize_jid("+18654375082") == "18654375082@s.whatsapp.net"
    assert WhatsAppBaileysService.normalize_jid("201234567890@s.whatsapp.net") == "201234567890@s.whatsapp.net"


@pytest.mark.asyncio
async def test_baileys_send_message_absorbs_kwargs():
    """Verify send_message safely absorbs extra kwargs without throwing."""
    service = WhatsAppBaileysService(session_id="session-123")
    service.client = MagicMock()
    service.client.send_message = AsyncMock(return_value={"status": "success", "message_id": "msg_999"})

    res = await service.send_message(
        to="18654375082",
        message="Hello from AI",
        messaging_type="RESPONSE",
        quick_replies=[{"title": "Yes"}]
    )

    assert res["status"] == "success"
    assert res["message_id"] == "msg_999"
    service.client.send_message.assert_awaited_once()


def test_orchestrator_resolves_baileys_whatsapp_client():
    """Verify AIOrchestrator instantiates WhatsAppBaileysService for Baileys connections."""
    mock_db = MagicMock()
    orchestrator = AIOrchestrator(mock_db)

    integration = Integration(
        id=uuid4(),
        project_id=uuid4(),
        provider="whatsapp",
        status=IntegrationStatus.CONNECTED,
        config={"whatsapp_provider": "baileys", "base_url": "https://ai-sales-bot-whatsapp-vdr6.onrender.com"},
        extra_data={"session_id": "session-xyz", "provider": "baileys"}
    )

    client = orchestrator._get_integration_client(integration)
    assert isinstance(client, WhatsAppBaileysService)
    assert client.session_id == "session-xyz"


def test_orchestrator_resolves_official_meta_whatsapp_client():
    """Verify AIOrchestrator instantiates WhatsAppService for official Meta connections."""
    mock_db = MagicMock()
    orchestrator = AIOrchestrator(mock_db)

    integration = Integration(
        id=uuid4(),
        project_id=uuid4(),
        provider="whatsapp",
        status=IntegrationStatus.CONNECTED,
        config={"whatsapp_provider": "business_api", "phone_number_id": "phone-123", "access_token": "token-456"},
        extra_data={}
    )

    client = orchestrator._get_integration_client(integration)
    assert isinstance(client, WhatsAppService)
    assert client.business_id == "phone-123"
    assert client.access_token == "token-456"


def test_service_factory_wa_gateway_support():
    """Verify service_factory creates WhatsAppBaileysService for baileys and wa_gateway."""
    svc_baileys = get_whatsapp_gateway_service(provider="baileys", base_url="http://localhost:3000")
    assert isinstance(svc_baileys, WhatsAppBaileysService)

    svc_gateway = get_whatsapp_gateway_service(provider="wa_gateway", base_url="http://localhost:3000")
    assert isinstance(svc_gateway, WhatsAppBaileysService)
