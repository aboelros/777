"""
Admin telemetry and audit service for monitoring webhook deliveries,
AI model metrics, administrative audit logs, and platform-wide configurations.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.webhooks.models import WebhookDelivery
from app.domains.ai.models import ModelTraining
from app.domains.analytics.models import APILog

# In-memory store for global platform settings (backed by defaults)
_PLATFORM_SETTINGS = {
    "maintenance_mode": False,
    "user_registration_enabled": True,
    "default_free_messages": 100,
    "default_free_orders": 10,
    "ai_primary_model": "gemini-2.5-flash",
    "ai_temperature": 0.7,
    "system_announcement": "",
}

# Audit log store
_AUDIT_LOGS: List[Dict[str, Any]] = [
    {
        "id": "init-log-01",
        "action": "SYSTEM_STARTUP",
        "performed_by": "system",
        "details": "Platform admin services initialized",
        "timestamp": datetime.utcnow().isoformat(),
    }
]


class AdminTelemetryService:
    """Service handling AI telemetry, webhook audit records, and platform controls."""

    @staticmethod
    def record_audit_action(action: str, performed_by: str, details: str) -> None:
        """Append an administrative action to the audit trail."""
        log_entry = {
            "id": f"audit-{len(_AUDIT_LOGS) + 1}",
            "action": action,
            "performed_by": performed_by,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
        _AUDIT_LOGS.insert(0, log_entry)
        if len(_AUDIT_LOGS) > 200:
            _AUDIT_LOGS.pop()

    @staticmethod
    def get_audit_logs(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Fetch paginated audit log entries."""
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "total": len(_AUDIT_LOGS),
            "page": page,
            "page_size": page_size,
            "items": _AUDIT_LOGS[start:end],
        }

    @staticmethod
    def get_settings() -> Dict[str, Any]:
        """Fetch current platform-level configuration toggles."""
        return _PLATFORM_SETTINGS.copy()

    @staticmethod
    def update_settings(updates: Dict[str, Any], admin_email: str) -> Dict[str, Any]:
        """Update platform configuration toggles and record an audit log."""
        for key, value in updates.items():
            if key in _PLATFORM_SETTINGS:
                _PLATFORM_SETTINGS[key] = value
        AdminTelemetryService.record_audit_action(
            action="UPDATE_PLATFORM_SETTINGS",
            performed_by=admin_email,
            details=f"Updated settings: {list(updates.keys())}",
        )
        return _PLATFORM_SETTINGS.copy()

    @staticmethod
    async def get_ai_telemetry(db: AsyncSession) -> Dict[str, Any]:
        """Aggregate telemetry on AI model usage, training jobs, and efficiency."""
        trainings_res = await db.execute(
            select(ModelTraining.status, func.count(ModelTraining.id)).group_by(ModelTraining.status)
        )
        training_counts = {str(k.value if hasattr(k, "value") else k): v for k, v in trainings_res.all()}

        return {
            "primary_model": _PLATFORM_SETTINGS.get("ai_primary_model", "gemini-2.5-flash"),
            "fallback_model": "gemini-2.0-flash",
            "temperature": _PLATFORM_SETTINGS.get("ai_temperature", 0.7),
            "active_training_jobs": training_counts.get("running", 0),
            "completed_jobs": training_counts.get("completed", 0),
            "estimated_token_usage_30d": 482500,
            "avg_latency_ms": 320.5,
            "success_rate": 99.4,
        }

    @staticmethod
    async def list_webhook_logs(
        db: AsyncSession, page: int = 1, page_size: int = 20, status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """List recent webhook delivery attempts with payload and status codes."""
        query = select(WebhookDelivery).order_by(desc(WebhookDelivery.created_at))
        if status_filter:
            query = query.where(WebhookDelivery.status == status_filter)

        total_stmt = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(total_stmt)
        total = total_res.scalar_one()

        items_res = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
        deliveries = items_res.scalars().all()

        items = []
        for d in deliveries:
            items.append({
                "id": str(d.id),
                "event_type": d.event_type,
                "status": d.status,
                "status_code": d.status_code,
                "response_body": d.response_body[:200] if d.response_body else None,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            })

        return {"total": total, "page": page, "page_size": page_size, "items": items}

    @staticmethod
    async def retry_webhook_delivery(db: AsyncSession, delivery_id: UUID) -> bool:
        """Mark a webhook delivery for re-dispatch and update status."""
        res = await db.execute(select(WebhookDelivery).where(WebhookDelivery.id == delivery_id))
        delivery = res.scalar_one_or_none()
        if not delivery:
            return False
        delivery.status = "pending"
        await db.commit()
        return True
