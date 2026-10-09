"""
Tenant-scoped performance, ROI, engagement trend, and AI insight helpers for report generation.
"""

from datetime import datetime
import json
from typing import Any, Dict, List, Optional
import structlog

from app.core.context import TenantContext
from app.domains.analytics.repository import ReportRepository, _require_tenant_context
from app.domains.integrations.models import IntegrationStatus
from app.domains.messages.models import Message, MessageDirection

logger = structlog.get_logger(__name__)


def _is_integration_active(integration: Any) -> bool:
    return bool(getattr(integration, "is_active", integration.status == IntegrationStatus.CONNECTED))


def serialize_report_order(order: Any) -> Dict[str, Any]:
    """Serialize an Order ORM instance or mock for order report details."""
    cust = getattr(order, "customer", None) or {}
    status_val = order.status.value if hasattr(order.status, "value") else order.status
    items = getattr(order, "line_items", None) or getattr(order, "items", None) or []
    return {
        "id": str(order.id),
        "external_id": order.external_id,
        "customer_name": getattr(order, "customer_name", cust.get("name")),
        "customer_email": getattr(order, "customer_email", cust.get("email")),
        "total": order.total,
        "currency": order.currency,
        "status": status_val,
        "provider": order.provider,
        "order_date": order.order_date.isoformat() if order.order_date else None,
        "items_count": len(items),
    }


def calculate_engagement_trend(messages: List[Message]) -> Dict[str, int]:
    """Calculate daily engagement trend from tenant-scoped messages."""
    trend: Dict[str, int] = {}
    for message in messages:
        if message.created_at:
            day_key = message.created_at.strftime("%Y-%m-%d")
            trend[day_key] = trend.get(day_key, 0) + 1
    return dict(sorted(trend.items()))


async def generate_performance_report_data(
    repo: ReportRepository,
    context: TenantContext,
    start_date: datetime,
    end_date: datetime,
) -> Dict[str, Any]:
    """Generate AI and system performance report strictly scoped to TenantContext."""
    ctx = _require_tenant_context(context, repo.context)
    logger.info("Generating performance report", project_id=str(ctx.project_id))

    messages = await repo.get_range_messages(start_date, end_date, context=ctx)
    ai_generated = sum(
        1
        for m in messages
        if getattr(m, "ai_generated", False) or (m.extra_data or {}).get("ai_generated", False)
    )
    total_outbound = sum(1 for m in messages if m.direction == MessageDirection.OUTBOUND)
    ai_usage_rate = (ai_generated / total_outbound * 100) if total_outbound > 0 else 0

    response_times = [
        (m.extra_data or {})["response_time"]
        for m in messages
        if (m.extra_data or {}).get("response_time")
    ]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0

    integrations = await repo.get_tenant_integrations(context=ctx)
    active_integrations = sum(1 for i in integrations if _is_integration_active(i))
    total_integrations = len(integrations)
    days = (end_date - start_date).days or 1

    return {
        "report_type": "performance",
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "ai_performance": {
            "ai_generated_messages": ai_generated,
            "total_outbound_messages": total_outbound,
            "ai_usage_rate": round(ai_usage_rate, 2),
            "average_response_time_seconds": round(avg_response_time, 2),
        },
        "integrations": {
            "total": total_integrations,
            "active": active_integrations,
            "inactive": total_integrations - active_integrations,
            "details": [
                {
                    "provider": i.provider,
                    "status": "active" if _is_integration_active(i) else "inactive",
                    "connected_at": i.created_at.isoformat() if i.created_at else None,
                }
                for i in integrations
            ],
        },
        "system_health": {
            "status": "healthy" if active_integrations > 0 else "warning",
            "uptime": "99.9%",
            "message_processing_rate": round(len(messages) / days, 2),
        },
    }


async def generate_roi_report_data(
    repo: ReportRepository,
    context: TenantContext,
    start_date: datetime,
    end_date: datetime,
) -> Dict[str, Any]:
    """Generate ROI report for AI automation strictly scoped to TenantContext."""
    ctx = _require_tenant_context(context, repo.context)
    logger.info("Generating ROI report", project_id=str(ctx.project_id))

    orders = await repo.get_range_orders(start_date, end_date, context=ctx)
    messages = await repo.get_range_messages(start_date, end_date, context=ctx)

    total_revenue = sum((order.total or 0.0) for order in orders)
    ai_messages = sum(
        1
        for m in messages
        if getattr(m, "ai_generated", False) or (m.extra_data or {}).get("ai_generated", False)
    )
    time_saved_hours = (ai_messages * 5) / 60
    cost_savings = time_saved_hours * 20
    total_conversations = len(set(m.customer_id for m in messages if m.customer_id))
    conversion_rate = (len(orders) / total_conversations * 100) if total_conversations > 0 else 0
    days = (end_date - start_date).days or 1

    return {
        "report_type": "roi",
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "revenue_impact": {
            "total_revenue": round(total_revenue, 2),
            "orders_processed": len(orders),
            "conversations_handled": total_conversations,
            "conversion_rate": round(conversion_rate, 2),
        },
        "automation_efficiency": {
            "ai_messages_sent": ai_messages,
            "time_saved_hours": round(time_saved_hours, 2),
            "estimated_cost_savings": round(cost_savings, 2),
            "automation_rate": round((ai_messages / len(messages) * 100) if messages else 0, 2),
        },
        "productivity_gains": {
            "messages_per_day": round(len(messages) / days, 2),
            "orders_per_day": round(len(orders) / days, 2),
            "revenue_per_conversation": (
                round(total_revenue / total_conversations, 2) if total_conversations > 0 else 0
            ),
        },
    }


async def generate_ai_insights_for_report(
    ai_provider: Optional[Any],
    context: TenantContext,
    report_data: Dict[str, Any],
    report_type: str,
) -> Dict[str, Any]:
    """Generate AI-powered insights for a validated tenant report."""
    _require_tenant_context(context)
    if not ai_provider:
        return {"error": "AI provider unavailable"}

    try:
        prompt = (
            f"Analyze this {report_type} report and provide actionable insights:\n\n"
            f"{report_data}\n\n"
            "Please provide:\n1. Key trends and patterns\n2. Areas of concern or opportunity\n"
            "3. Specific actionable recommendations\n4. Predicted outcomes if recommendations are followed\n\n"
            "Format as structured JSON with keys: trends, concerns, recommendations, predictions"
        )
        response = await ai_provider.generate_response(
            prompt=prompt, use_functions=False, temperature=0.3
        )
        raw_text = (
            response.text
            if hasattr(response, "text")
            else (response.get("text", "") if isinstance(response, dict) else str(response))
        )
        try:
            return json.loads(raw_text)
        except Exception:
            return {"summary": raw_text, "generated_at": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error("Failed to generate AI insights", error=str(e))
        return {"error": "AI insights unavailable"}
