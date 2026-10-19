"""
Webhook project resolution service with strict multi-tenant deterministic binding.
"""

from typing import Dict, Any, Optional, List, Set
from uuid import UUID
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.integrations.models import Integration, IntegrationStatus
from app.services.webhook_domain import WebhookEvent

logger = structlog.get_logger(__name__)


class WebhookProjectResolver:
    """Deterministically maps incoming webhook events to tenant projects."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def resolve_project(
        self,
        event: WebhookEvent,
        explicit_project_id: Optional[UUID] = None
    ) -> Optional[str]:
        """Find the tenant project ID deterministically or return None."""
        if explicit_project_id:
            return await self._resolve_explicit(explicit_project_id, event.channel)

        if event.platform == "meta":
            return await self._resolve_meta(event)

        if event.platform == "wa_gateway":
            return await self._resolve_wa_gateway(event)

        if event.platform == "telegram":
            return await self._resolve_telegram(event)

        if event.platform == "shopify":
            return await self._resolve_shopify(event)

        logger.warning(
            "No deterministic tenant mapping found",
            platform=event.platform,
            channel=event.channel,
            event_id=event.event_id
        )
        return None

    async def _resolve_explicit(self, project_id: UUID, channel: str) -> Optional[str]:
        query = select(Integration).where(
            Integration.project_id == project_id,
            Integration.provider == channel,
            Integration.status == IntegrationStatus.CONNECTED
        )
        result = await self.db.execute(query)
        integrations = result.scalars().all()
        if integrations:
            return str(project_id)
        logger.warning("No connected integration found for explicit project", project_id=str(project_id), channel=channel)
        return None

    async def _resolve_meta(self, event: WebhookEvent) -> Optional[str]:
        if event.channel == "whatsapp":
            return await self._resolve_meta_whatsapp(event)
        if event.channel == "instagram":
            return await self._resolve_meta_instagram(event)
        if event.channel == "facebook":
            return await self._resolve_meta_facebook(event)
        return None

    async def _resolve_meta_whatsapp(self, event: WebhookEvent) -> Optional[str]:
        phone_id = event.payload.get("metadata", {}).get("phone_number_id")
        if not phone_id:
            return None

        query = select(Integration).where(
            Integration.provider == "whatsapp",
            Integration.status == IntegrationStatus.CONNECTED
        )
        result = await self.db.execute(query)
        matched_projects: List[UUID] = []
        for it in result.scalars().all():
            cfg = it.config or {}
            ext = it.extra_data or {}
            stored_phone = str(ext.get("phone_number_id") or cfg.get("phone_number_id") or "")
            if stored_phone == str(phone_id):
                matched_projects.append(it.project_id)

        return self._deduplicate_match(matched_projects, f"phone_number_id {phone_id}")

    async def _resolve_meta_instagram(self, event: WebhookEvent) -> Optional[str]:
        raw_entry = (event.raw_data or {}).get("entry", [{}])[0] if isinstance((event.raw_data or {}).get("entry"), list) and (event.raw_data or {}).get("entry") else {}
        payload_entry = event.payload.get("entry", [{}])[0] if isinstance(event.payload.get("entry"), list) and event.payload.get("entry") else {}
        messaging_entry = raw_entry.get("messaging", [{}])[0] if isinstance(raw_entry.get("messaging"), list) and raw_entry.get("messaging") else {}

        target_ids = {
            str(event.payload.get("page_id") or "").strip(),
            str(raw_entry.get("id") or "").strip(),
            str(payload_entry.get("id") or "").strip(),
            str(messaging_entry.get("recipient", {}).get("id") or "").strip()
        } - {"", "None", "unknown"}

        if not target_ids:
            return None

        query = select(Integration).where(
            Integration.provider.in_(["instagram", "facebook", "meta"]),
            Integration.status == IntegrationStatus.CONNECTED
        )
        result = await self.db.execute(query)
        integrations = result.scalars().all()
        matched_projects: List[UUID] = []
        for it in integrations:
            cfg = it.config or {}
            ext = it.extra_data or {}
            stored_ids = {
                str(cfg.get("instagram_business_account_id") or "").strip(),
                str(ext.get("instagram_business_account_id") or "").strip(),
                str(cfg.get("page_id") or "").strip(),
                str(ext.get("page_id") or "").strip()
            } - {"", "None"}
            if target_ids & stored_ids:
                matched_projects.append(it.project_id)

        res = self._deduplicate_match(matched_projects, f"instagram targets {target_ids}")
        if res:
            return res

        # Fallback: if only one project has a connected Instagram/Facebook integration, route to it
        candidate_projects = list({it.project_id for it in integrations})
        if len(candidate_projects) == 1:
            logger.info("Fallback matched single connected Meta integration", project_id=str(candidate_projects[0]))
            return str(candidate_projects[0])

        return None

    async def _resolve_meta_facebook(self, event: WebhookEvent) -> Optional[str]:
        raw_entry = (event.raw_data or {}).get("entry", [{}])[0] if isinstance((event.raw_data or {}).get("entry"), list) and (event.raw_data or {}).get("entry") else {}
        payload_entry = event.payload.get("entry", [{}])[0] if isinstance(event.payload.get("entry"), list) and event.payload.get("entry") else {}
        messaging_entry = raw_entry.get("messaging", [{}])[0] if isinstance(raw_entry.get("messaging"), list) and raw_entry.get("messaging") else {}

        target_ids = {
            str(event.payload.get("page_id") or "").strip(),
            str(raw_entry.get("id") or "").strip(),
            str(payload_entry.get("id") or "").strip(),
            str(messaging_entry.get("recipient", {}).get("id") or "").strip()
        } - {"", "None", "unknown"}

        if not target_ids:
            return None

        query = select(Integration).where(
            Integration.provider.in_(["facebook", "meta"]),
            Integration.status == IntegrationStatus.CONNECTED
        )
        result = await self.db.execute(query)
        matched_projects: List[UUID] = []
        for it in result.scalars().all():
            cfg = it.config or {}
            ext = it.extra_data or {}
            stored_ids = {
                str(cfg.get("page_id") or "").strip(),
                str(ext.get("page_id") or "").strip()
            } - {"", "None"}
            if target_ids & stored_ids:
                matched_projects.append(it.project_id)

        return self._deduplicate_match(matched_projects, f"facebook targets {target_ids}")

    async def _resolve_wa_gateway(self, event: WebhookEvent) -> Optional[str]:
        session_id = str(event.payload.get("session_id") or "").strip()
        if not session_id:
            return None

        query = select(Integration).where(
            Integration.provider == "whatsapp",
            Integration.status == IntegrationStatus.CONNECTED
        )
        result = await self.db.execute(query)
        matched_projects: List[UUID] = []
        for it in result.scalars().all():
            ext = it.extra_data or {}
            if ext.get("provider") == "wa_gateway" and str(ext.get("session_id") or "").strip() == session_id:
                matched_projects.append(it.project_id)

        return self._deduplicate_match(matched_projects, f"session_id {session_id}")

    async def _resolve_telegram(self, event: WebhookEvent) -> Optional[str]:
        bot_username = str(event.payload.get("bot_username") or "").strip().lower()
        query = select(Integration).where(
            Integration.provider == "telegram",
            Integration.status == IntegrationStatus.CONNECTED
        )
        result = await self.db.execute(query)
        matched_projects: List[UUID] = []
        for it in result.scalars().all():
            cfg = it.config or {}
            if bot_username and str(cfg.get("bot_username") or "").strip().lower() == bot_username:
                matched_projects.append(it.project_id)

        return self._deduplicate_match(matched_projects, f"telegram {bot_username}")

    async def _resolve_shopify(self, event: WebhookEvent) -> Optional[str]:
        shop_domain = str(event.payload.get("shop_domain") or "").strip().lower()
        if not shop_domain:
            return None

        query = select(Integration).where(
            Integration.provider == "shopify",
            Integration.status == IntegrationStatus.CONNECTED
        )
        result = await self.db.execute(query)
        matched_projects: List[UUID] = []
        for it in result.scalars().all():
            cfg = it.config or {}
            if str(cfg.get("shop_domain") or "").strip().lower() == shop_domain:
                matched_projects.append(it.project_id)

        return self._deduplicate_match(matched_projects, f"shopify domain {shop_domain}")

    def _deduplicate_match(self, matched_projects: List[UUID], identifier: str) -> Optional[str]:
        unique = list(dict.fromkeys(matched_projects))
        if len(unique) == 1:
            return str(unique[0])
        if len(unique) > 1:
            logger.error("Ambiguous mapping: Multiple projects match identifier", identifier=identifier, count=len(unique))
            return None
        logger.warning("No matching project found for identifier", identifier=identifier)
        return None
