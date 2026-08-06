import hmac
import hashlib
import json
import httpx
import structlog
from typing import Dict, Any, List
from uuid import UUID
from sqlalchemy import select

from app.core.uow import UnitOfWork
from app.domains.webhooks.models import WebhookEndpoint, WebhookDelivery

logger = structlog.get_logger(__name__)

class EventDispatcher:
    """
    Dispatches internal platform events to registered external WebhookEndpoints.
    Enforces security via HMAC-SHA256 signatures.
    """
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def dispatch(self, project_id: UUID, event_type: str, payload: Dict[str, Any]):
        """Finds subscribed webhooks for a project and dispatches the event."""
        logger.info(f"Dispatching event: {event_type}", project_id=str(project_id))
        
        async with self.uow as uow:
            # Find active webhooks for this project
            stmt = select(WebhookEndpoint).where(
                WebhookEndpoint.project_id == project_id,
                WebhookEndpoint.is_active == True
            )
            result = await uow.session.execute(stmt)
            endpoints = result.scalars().all()
            
            # Filter endpoints that subscribed to this specific event (or wildcard "*")
            subscribed = [
                ep for ep in endpoints 
                if event_type in ep.events or "*" in ep.events
            ]
            
            if not subscribed:
                logger.debug(f"No webhooks subscribed for {event_type}")
                return
                
            for endpoint in subscribed:
                await self._send_webhook(uow.session, endpoint, event_type, payload)

    async def _send_webhook(self, session, endpoint: WebhookEndpoint, event_type: str, payload: Dict[str, Any]):
        """Sends the HTTP request and logs the delivery attempt."""
        # Prepare the payload with event metadata
        full_payload = {
            "event": event_type,
            "data": payload
        }
        payload_bytes = json.dumps(full_payload).encode('utf-8')
        
        # Calculate HMAC signature using the endpoint secret
        signature = hmac.new(
            endpoint.secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "Content-Type": "application/json",
            "X-AntiGravity-Signature": signature,
            "X-AntiGravity-Event": event_type
        }
        
        # Create a delivery record before sending
        delivery = WebhookDelivery(
            endpoint_id=endpoint.id,
            event_type=event_type,
            payload=full_payload,
            status="pending"
        )
        session.add(delivery)
        await session.commit()
        
        try:
            # In a real system, this would be queued via Celery to avoid blocking
            # but for this MVP architecture we fire and forget inline.
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(endpoint.url, content=payload_bytes, headers=headers)
                
            delivery.status = "success" if response.status_code < 400 else "failed"
            delivery.status_code = str(response.status_code)
            delivery.response_body = response.text[:1000] # truncate
            
        except Exception as e:
            logger.error("Webhook delivery failed", endpoint_id=str(endpoint.id), error=str(e))
            delivery.status = "failed"
            delivery.response_body = str(e)
            
        await session.commit()
