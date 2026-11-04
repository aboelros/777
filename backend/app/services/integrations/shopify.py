"""
Shopify integration service.
Handles authenticated API communication, webhook signature validation,
catalog retrieval, and order synchronization.
"""

import hmac
import hashlib
import base64
from typing import Dict, Any, List, Optional, Union
import httpx
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)


class ShopifyService:
    """Service for Shopify Admin API integration and webhook management."""

    def __init__(
        self,
        shop_url: Optional[Union[str, Dict[str, Any]]] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        **kwargs
    ):
        """Initialize Shopify service with credentials or config dict."""
        if isinstance(shop_url, dict):
            cfg = shop_url
            raw_url = cfg.get("shop_url") or cfg.get("shop_domain", "")
            self.api_key = cfg.get("api_key")
            self.api_secret = cfg.get("api_secret") or settings.SHOPIFY_API_SECRET
            self.access_token = cfg.get("access_token") or cfg.get("token")
        else:
            raw_url = shop_url or ""
            self.api_key = api_key
            self.api_secret = api_secret or settings.SHOPIFY_API_SECRET
            self.access_token = access_token or kwargs.get("token")

        # Normalize shop domain
        cleaned = raw_url.replace("https://", "").replace("http://", "").strip("/")
        if cleaned and not cleaned.endswith(".myshopify.com") and "." not in cleaned:
            cleaned = f"{cleaned}.myshopify.com"
        self.shop_url = cleaned
        self.api_version = "2024-01"

    def verify_webhook(self, data: bytes, hmac_header: str) -> bool:
        """Verify Shopify webhook HMAC-SHA256 signature (Base64 encoded)."""
        if not self.api_secret or not hmac_header:
            return False
        computed_hmac = base64.b64encode(
            hmac.new(self.api_secret.encode("utf-8"), data, hashlib.sha256).digest()
        ).decode("utf-8")
        return hmac.compare_digest(computed_hmac, hmac_header.strip())

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Authenticated HTTP request with OAuth Access Token or Basic Auth."""
        if not self.shop_url:
            raise ValueError("Shopify shop_url is not configured")

        url = f"https://{self.shop_url}/admin/api/{self.api_version}/{endpoint}"
        headers = {"Content-Type": "application/json"}
        auth = None

        if self.access_token:
            headers["X-Shopify-Access-Token"] = self.access_token
        elif self.api_key and self.api_secret:
            auth = (self.api_key, self.api_secret)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method,
                    url,
                    headers=headers,
                    auth=auth,
                    params=params,
                    json=json_data,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error("Shopify API request failed", error=str(e), endpoint=endpoint)
                raise

    async def fetch_orders(
        self,
        limit: int = 50,
        status: str = "any",
        since_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch orders from Shopify store."""
        params: Dict[str, Any] = {"limit": limit, "status": status}
        if since_id:
            params["since_id"] = since_id
        try:
            data = await self._make_request("GET", "orders.json", params=params)
            return data.get("orders", [])
        except Exception as e:
            logger.error("Failed to fetch Shopify orders", error=str(e))
            return []

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get order details by Shopify order ID."""
        try:
            data = await self._make_request("GET", f"orders/{order_id}.json")
            return data.get("order", {})
        except Exception as e:
            logger.error("Failed to fetch Shopify order", order_id=order_id, error=str(e))
            return {}

    async def update_order(
        self,
        order_id: str,
        status_or_data: Any,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update order status or metadata in Shopify."""
        if isinstance(status_or_data, dict):
            payload = {"order": status_or_data}
        else:
            body: Dict[str, Any] = {"note": note} if note else {}
            if status_or_data:
                body["financial_status"] = status_or_data
            payload = {"order": body}

        try:
            res = await self._make_request("PUT", f"orders/{order_id}.json", json_data=payload)
            return res.get("order", {})
        except Exception as e:
            logger.error("Failed to update Shopify order", order_id=order_id, error=str(e))
            return {}

    async def fetch_products(self, limit: int = 50, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch product catalog from Shopify store."""
        params: Dict[str, Any] = {"limit": limit}
        if query:
            params["title"] = query
        try:
            data = await self._make_request("GET", "products.json", params=params)
            return data.get("products", [])
        except Exception as e:
            logger.error("Failed to fetch Shopify products", error=str(e))
            return []

    async def check_inventory(self, product_id_or_title: str) -> Dict[str, Any]:
        """Check live stock quantity for a product."""
        products = await self.fetch_products(limit=5, query=product_id_or_title)
        if not products:
            return {"found": False, "in_stock": False, "stock_quantity": 0}

        prod = products[0]
        total_stock = sum(v.get("inventory_quantity", 0) for v in prod.get("variants", []))
        unit_price = float(prod.get("variants", [{}])[0].get("price", 0.0))
        return {
            "found": True,
            "product_id": str(prod.get("id")),
            "product_name": prod.get("title"),
            "in_stock": total_stock > 0,
            "stock_quantity": total_stock,
            "unit_price": unit_price
        }

    def transform_order(self, shopify_order: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Shopify order format to internal schema."""
        return {
            "external_id": str(shopify_order.get("id")),
            "provider": "shopify",
            "status": shopify_order.get("financial_status") or "pending",
            "customer": {
                "name": (
                    shopify_order.get("customer", {}).get("first_name", "") + " " +
                    shopify_order.get("customer", {}).get("last_name", "")
                ).strip() or shopify_order.get("customer", {}).get("name"),
                "email": shopify_order.get("customer", {}).get("email"),
                "phone": shopify_order.get("customer", {}).get("phone"),
            },
            "items": [
                {
                    "name": item.get("name"),
                    "quantity": item.get("quantity"),
                    "price": float(item.get("price", 0)),
                    "sku": item.get("sku"),
                }
                for item in shopify_order.get("line_items", [])
            ],
            "total": float(shopify_order.get("total_price", 0)),
            "currency": shopify_order.get("currency", "USD"),
            "metadata": {
                "order_number": shopify_order.get("order_number"),
                "fulfillment_status": shopify_order.get("fulfillment_status"),
                "tags": shopify_order.get("tags"),
            },
        }

    @staticmethod
    def get_webhook_topics() -> List[str]:
        """Get standard Shopify webhook subscription topics."""
        return [
            "orders/create",
            "orders/updated",
            "orders/fulfilled",
            "orders/cancelled",
            "products/create",
            "products/update"
        ]
