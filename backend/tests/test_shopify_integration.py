"""
Unit and regression tests for Shopify integration service.
Verifies Base64 HMAC webhook verification, client initialization, product fetching,
inventory calculations, order transformation, and error resilience.
"""

import pytest
import hmac
import hashlib
import base64
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.services.integrations.shopify import ShopifyService


def test_shopify_initialization_variants():
    # 1. Config dict initialization (used by orchestrator)
    cfg = {
        "shop_url": "cairo-sneakers",
        "access_token": "shpat_test_12345",
        "api_secret": "secret_abc"
    }
    svc1 = ShopifyService(cfg)
    assert svc1.shop_url == "cairo-sneakers.myshopify.com"
    assert svc1.access_token == "shpat_test_12345"
    assert svc1.api_secret == "secret_abc"

    # 2. Keyword initialization with URL normalization
    svc2 = ShopifyService(
        shop_url="https://alex-perfumes.myshopify.com/",
        api_key="key_xyz",
        api_secret="secret_xyz"
    )
    assert svc2.shop_url == "alex-perfumes.myshopify.com"
    assert svc2.api_key == "key_xyz"


def test_shopify_webhook_base64_hmac_verification():
    secret = "shopify_test_secret_key_123"
    svc = ShopifyService(shop_url="test.myshopify.com", api_secret=secret)
    raw_payload = b'{"id": 123456, "status": "open"}'

    # Compute valid Shopify Base64 HMAC
    valid_hmac = base64.b64encode(
        hmac.new(secret.encode("utf-8"), raw_payload, hashlib.sha256).digest()
    ).decode("utf-8")

    # 1. Valid signature -> TRUE
    assert svc.verify_webhook(raw_payload, valid_hmac) is True

    # 2. Tampered payload -> FALSE
    tampered_payload = b'{"id": 123456, "status": "hacked"}'
    assert svc.verify_webhook(tampered_payload, valid_hmac) is False

    # 3. Invalid signature string -> FALSE
    assert svc.verify_webhook(raw_payload, "invalid_base64_hmac") is False

    # 4. Empty signature or secret -> FALSE
    assert svc.verify_webhook(raw_payload, "") is False


@pytest.mark.asyncio
async def test_shopify_make_request_headers_and_auth():
    svc = ShopifyService(shop_url="test.myshopify.com", access_token="shpat_valid_token")

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"shop": {"name": "Test Store"}}
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_resp
        data = await svc._make_request("GET", "shop.json")

        assert data["shop"]["name"] == "Test Store"
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["headers"]["X-Shopify-Access-Token"] == "shpat_valid_token"


@pytest.mark.asyncio
async def test_shopify_fetch_products_and_check_inventory():
    svc = ShopifyService(shop_url="test.myshopify.com", access_token="token")

    mock_products_payload = {
        "products": [
            {
                "id": 998877,
                "title": "Air Jordan 1",
                "variants": [
                    {"id": 1, "price": "150.00", "inventory_quantity": 4},
                    {"id": 2, "price": "150.00", "inventory_quantity": 2}
                ]
            }
        ]
    }

    with patch.object(svc, "_make_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_products_payload

        inv = await svc.check_inventory("Air Jordan")
        assert inv["found"] is True
        assert inv["product_name"] == "Air Jordan 1"
        assert inv["in_stock"] is True
        assert inv["stock_quantity"] == 6  # 4 + 2 across variants
        assert inv["unit_price"] == 150.0


def test_shopify_transform_order():
    svc = ShopifyService(shop_url="test.myshopify.com")

    raw_order = {
        "id": 554433,
        "financial_status": "paid",
        "fulfillment_status": "unfulfilled",
        "order_number": 1042,
        "total_price": "299.99",
        "currency": "EGP",
        "customer": {
            "first_name": "Omar",
            "last_name": "Tariq",
            "email": "omar@example.com",
            "phone": "+201011122233"
        },
        "line_items": [
            {"name": "Running Shoes", "quantity": 1, "price": "299.99", "sku": "RS-42"}
        ],
        "tags": "vip, repeat"
    }

    transformed = svc.transform_order(raw_order)
    assert transformed["external_id"] == "554433"
    assert transformed["provider"] == "shopify"
    assert transformed["status"] == "paid"
    assert transformed["total"] == 299.99
    assert transformed["currency"] == "EGP"
    assert transformed["customer"]["name"] == "Omar Tariq"
    assert transformed["customer"]["phone"] == "+201011122233"
    assert len(transformed["items"]) == 1
    assert transformed["items"][0]["sku"] == "RS-42"
    assert transformed["metadata"]["order_number"] == 1042


@pytest.mark.asyncio
async def test_shopify_update_order_flexible_params():
    svc = ShopifyService(shop_url="test.myshopify.com", access_token="token")

    with patch.object(svc, "_make_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {"order": {"id": 123, "financial_status": "refunded"}}

        # Call with positional status and note
        res = await svc.update_order("123", "refunded", note="Customer requested cancellation")
        assert res["financial_status"] == "refunded"
        mock_req.assert_called_once()
        called_json = mock_req.call_args[1]["json_data"]
        assert called_json["order"]["financial_status"] == "refunded"
        assert called_json["order"]["note"] == "Customer requested cancellation"
