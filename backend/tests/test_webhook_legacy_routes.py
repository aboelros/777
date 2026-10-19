import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

pytestmark = pytest.mark.asyncio

async def test_legacy_webhook_routes_do_not_crash_with_name_error():
    """
    Regression test: Ensure legacy webhook endpoints (/whatsapp, /go-whatsapp,
    /whatsapp/go_whatsapp, /tiktok, /discord) do not raise runtime NameError
    from referencing undefined project_id parameter.
    """
    endpoints = [
        "/api/v1/webhooks/whatsapp",
        "/api/v1/webhooks/go-whatsapp",
        "/api/v1/webhooks/whatsapp/go_whatsapp",
        "/api/v1/webhooks/tiktok",
        "/api/v1/webhooks/discord",
    ]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for endpoint in endpoints:
            response = await client.post(endpoint, json={"event": "test"})
            # Verify status is NOT 500 (NameError). Should be handled by WebhookGateway (200, 401, or 403)
            assert response.status_code != 500, f"Endpoint {endpoint} failed with 500 error: {response.text}"
            assert response.status_code in [200, 400, 401, 403], f"Unexpected status {response.status_code} on {endpoint}"
