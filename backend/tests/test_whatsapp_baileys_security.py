"""
Security and tenant isolation tests for WhatsApp Baileys integration.
"""

import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import HTTPException

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.v1.whatsapp_session_helpers import get_whatsapp_integration
from app.services.integrations.whatsapp_business import WhatsAppBusinessService


@pytest.mark.asyncio
async def test_tenant_isolation_on_session_access():
    """Verify tenant isolation: users cannot query integrations belonging to other projects."""
    tenant_project_id = uuid4()
    foreign_project_id = uuid4()
    integration_id = uuid4()

    mock_db = MagicMock()
    mock_db.execute = AsyncMock()

    # Case 1: Querying with mismatched project_id returns None from DB -> 404
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await get_whatsapp_integration(mock_db, foreign_project_id, integration_id)
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()

    # Case 2: Matching project_id returns the integration successfully
    mock_integration = MagicMock(
        id=integration_id,
        project_id=tenant_project_id,
        provider="whatsapp"
    )
    mock_result.scalar_one_or_none.return_value = mock_integration

    result = await get_whatsapp_integration(mock_db, tenant_project_id, integration_id)
    assert result.id == integration_id
    assert result.project_id == tenant_project_id

    # Case 3: Integration with wrong provider returns 400
    mock_wrong_provider = MagicMock(
        id=integration_id,
        project_id=tenant_project_id,
        provider="telegram"
    )
    mock_result.scalar_one_or_none.return_value = mock_wrong_provider
    with pytest.raises(HTTPException) as exc_info:
        await get_whatsapp_integration(mock_db, tenant_project_id, integration_id)
    assert exc_info.value.status_code == 400
    assert "not a whatsapp provider" in exc_info.value.detail.lower()


def test_cloud_api_regression():
    """Verify official WhatsApp Business API service webhook parsing remains intact."""
    official_service = WhatsAppBusinessService.__new__(WhatsAppBusinessService)
    
    meta_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WHATSAPP_BIZ_ACCOUNT_123",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "15550192834"},
                    "contacts": [{"profile": {"name": "Official User"}, "wa_id": "15550192834"}],
                    "messages": [{
                        "from": "15550192834",
                        "id": "wamid.HBgL",
                        "timestamp": "1730000200",
                        "text": {"body": "Testing official Cloud API"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }

    parsed = official_service.parse_webhook(meta_payload)
    assert parsed is not None
    assert parsed["message_id"] == "wamid.HBgL"
    assert parsed["from"] == "15550192834"
    assert parsed["text"] == "Testing official Cloud API"
    assert parsed["contact"]["name"] == "Official User"
