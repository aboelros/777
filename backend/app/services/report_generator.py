"""
Advanced Report Generation Service with AI-powered insights.
Generates comprehensive analytics reports strictly scoped to TenantContext.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import TenantContext
from app.domains.analytics.repository import ReportRepository, _require_tenant_context
from app.domains.messages.models import Message, MessageDirection
from app.domains.orders.models import OrderStatus
from app.services.report_insights import (
    calculate_engagement_trend,
    generate_ai_insights_for_report,
    generate_performance_report_data,
    generate_roi_report_data,
    serialize_report_order,
)
from app.services.service_factory import get_ai_provider

logger = structlog.get_logger(__name__)


class ReportGenerator:
    """Generate comprehensive analytics reports with AI insights under TenantContext."""

    def __init__(
        self,
        db: AsyncSession,
        project_id: Optional[Union[UUID, TenantContext]] = None,
        context: Optional[TenantContext] = None,
    ):
        if isinstance(project_id, TenantContext) and context is None:
            context = project_id
            project_id = context.project_id

        ctx = _require_tenant_context(context)
        if project_id is not None and UUID(str(project_id)) != ctx.project_id:
            raise PermissionError("Caller project_id does not match authenticated TenantContext")

        self.db = db
        self.context = ctx
        self.project_id = ctx.project_id
        self.repo = ReportRepository(db, ctx)

        try:
            self.ai_provider = get_ai_provider(db)
        except Exception as exc:
            logger.warning("AI provider unavailable for report insights", error=str(exc))
            self.ai_provider = None

    async def generate_sales_report(
        self, start_date: datetime, end_date: datetime, include_ai_insights: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive sales report scoped to TenantContext."""
        logger.info("Generating sales report", project_id=str(self.project_id))
        orders = await self.repo.get_range_orders(start_date, end_date, context=self.context)

        total_revenue = sum((order.total or 0.0) for order in orders)
        total_orders = len(orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        status_breakdown = {
            status.value: sum(1 for o in orders if o.status in (status, status.value))
            for status in OrderStatus
        }

        revenue_by_day: Dict[str, float] = {}
        for order in orders:
            if order.order_date:
                day_key = order.order_date.strftime("%Y-%m-%d")
                revenue_by_day[day_key] = revenue_by_day.get(day_key, 0.0) + (order.total or 0.0)

        report: Dict[str, Any] = {
            "report_type": "sales",
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "summary": {
                "total_revenue": round(total_revenue, 2),
                "total_orders": total_orders,
                "average_order_value": round(avg_order_value, 2),
                "currency": (orders[0].currency if orders and orders[0].currency else "USD"),
            },
            "status_breakdown": status_breakdown,
            "revenue_by_day": revenue_by_day,
            "top_performing_days": sorted(
                revenue_by_day.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }

        if include_ai_insights and orders:
            report["ai_insights"] = await self._generate_ai_insights(report, "sales")

        return report

    async def generate_order_report(
        self, start_date: datetime, end_date: datetime, include_details: bool = True
    ) -> Dict[str, Any]:
        """Generate detailed order tracking and analytics report scoped to TenantContext."""
        logger.info("Generating order report", project_id=str(self.project_id))
        orders = await self.repo.get_range_orders(
            start_date, end_date, context=self.context, desc_order=True
        )

        total_orders = len(orders)
        fulfilled_orders = sum(
            1 for o in orders if o.status in (OrderStatus.FULFILLED, OrderStatus.FULFILLED.value)
        )
        cancelled_orders = sum(
            1 for o in orders if o.status in (OrderStatus.CANCELLED, OrderStatus.CANCELLED.value)
        )
        pending_orders = sum(
            1 for o in orders if o.status in (OrderStatus.PENDING, OrderStatus.PENDING.value)
        )

        fulfillment_rate = (fulfilled_orders / total_orders * 100) if total_orders > 0 else 0
        cancellation_rate = (cancelled_orders / total_orders * 100) if total_orders > 0 else 0

        provider_breakdown: Dict[str, int] = {}
        for order in orders:
            provider = order.provider or "manual"
            provider_breakdown[provider] = provider_breakdown.get(provider, 0) + 1

        report: Dict[str, Any] = {
            "report_type": "orders",
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "summary": {
                "total_orders": total_orders,
                "fulfilled_orders": fulfilled_orders,
                "cancelled_orders": cancelled_orders,
                "pending_orders": pending_orders,
                "fulfillment_rate": round(fulfillment_rate, 2),
                "cancellation_rate": round(cancellation_rate, 2),
            },
            "provider_breakdown": provider_breakdown,
            "status_distribution": {
                status.value: sum(1 for o in orders if o.status in (status, status.value))
                for status in OrderStatus
            },
        }

        if include_details:
            report["orders"] = [serialize_report_order(order) for order in orders[:50]]

        return report

    async def generate_customer_report(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate customer analytics and engagement report scoped to TenantContext."""
        logger.info("Generating customer report", project_id=str(self.project_id))
        messages = await self.repo.get_range_messages(start_date, end_date, context=self.context)

        total_messages = len(messages)
        inbound = sum(1 for m in messages if m.direction == MessageDirection.INBOUND)
        outbound = sum(1 for m in messages if m.direction == MessageDirection.OUTBOUND)

        channel_usage: Dict[str, int] = {}
        for msg in messages:
            ch = getattr(msg, "channel", None) or msg.platform or msg.provider or "unknown"
            channel_usage[ch] = channel_usage.get(ch, 0) + 1

        unique_custs = len(set(m.customer_id for m in messages if m.customer_id))
        response_rate = (outbound / inbound * 100) if inbound > 0 else 0
        avg_msgs = round(total_messages / unique_custs, 2) if unique_custs > 0 else 0

        return {
            "report_type": "customers",
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "summary": {
                "total_messages": total_messages,
                "inbound_messages": inbound,
                "outbound_messages": outbound,
                "unique_customers": unique_custs,
                "response_rate": round(response_rate, 2),
                "avg_messages_per_customer": avg_msgs,
            },
            "channel_usage": channel_usage,
            "engagement_trend": await self._calculate_engagement_trend(messages),
        }

    async def generate_performance_report(self, start: datetime, end: datetime) -> Dict[str, Any]:
        return await generate_performance_report_data(self.repo, self.context, start, end)

    async def generate_roi_report(self, start: datetime, end: datetime) -> Dict[str, Any]:
        return await generate_roi_report_data(self.repo, self.context, start, end)

    async def _generate_ai_insights(self, data: Dict[str, Any], rtype: str) -> Dict[str, Any]:
        return await generate_ai_insights_for_report(self.ai_provider, self.context, data, rtype)

    async def _calculate_engagement_trend(self, messages: List[Message]) -> Dict[str, int]:
        return calculate_engagement_trend(messages)


async def generate_report(
    db: AsyncSession,
    project_id: Optional[UUID] = None,
    report_type: str = "sales",
    date_range: str = "last_30_days",
    context: Optional[TenantContext] = None,
    **options,
) -> Dict[str, Any]:
    """Main entry point for report generation requiring TenantContext."""
    ctx = _require_tenant_context(context)
    if project_id is not None and UUID(str(project_id)) != ctx.project_id:
        raise PermissionError("Caller project_id does not match authenticated TenantContext")

    if options.get("start_date") is not None and options.get("end_date") is not None:
        start_date = options["start_date"]
        end_date = options["end_date"]
    else:
        end_date = datetime.utcnow()
        if date_range == "last_7_days":
            start_date = end_date - timedelta(days=7)
        elif date_range == "last_30_days":
            start_date = end_date - timedelta(days=30)
        elif date_range == "last_month":
            start_date = (end_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        elif date_range == "custom":
            start_date = options.get("start_date", end_date - timedelta(days=30))
            end_date = options.get("end_date", end_date)
        else:
            start_date = end_date - timedelta(days=30)

    if start_date > end_date:
        raise ValueError("start_date must not be after end_date")

    generator = ReportGenerator(db, project_id=ctx.project_id, context=ctx)
    handlers = {
        "sales": generator.generate_sales_report,
        "orders": generator.generate_order_report,
        "customers": generator.generate_customer_report,
        "performance": generator.generate_performance_report,
        "roi": generator.generate_roi_report,
    }
    if report_type not in handlers:
        raise ValueError(f"Unknown report type: {report_type}")
    return await handlers[report_type](start_date, end_date)
