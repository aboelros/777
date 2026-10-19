"""
Tenant-scoped Analytics & Reporting domain service.
Enforces TenantContext before any repository query or external provider call.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.context import TenantContext
from app.core.uow import UnitOfWork
from app.domains.analytics.models import Report
from app.domains.analytics.repository import (
    APILogRepository,
    ReportRepository,
    _require_tenant_context,
)
from app.services.integrations import facebook as _fb_module
from app.services.integrations import instagram as _ig_module
from app.services.report_generator import generate_report as generate_report_service

logger = structlog.get_logger(__name__)

FacebookClient = _fb_module.FacebookClient
InstagramClient = _ig_module.InstagramClient


def generate_report_summary(report_type: str, payload: Dict[str, Any]) -> str:
    """Generate human-readable summary from report payload."""
    if report_type == "sales" and "summary" in payload:
        summary = payload["summary"]
        return (
            f"Generated {summary.get('total_orders', 0)} orders with "
            f"${summary.get('total_revenue', 0.0):.2f} in total revenue. "
            f"Average order value: ${summary.get('average_order_value', 0.0):.2f}."
        )
    if report_type == "messages" and "summary" in payload:
        summary = payload["summary"]
        return (
            f"Processed {summary.get('total_messages', 0)} messages "
            f"({summary.get('inbound_messages', 0)} inbound, "
            f"{summary.get('outbound_messages', 0)} outbound). "
            f"AI automation rate: {summary.get('automation_rate', 0.0):.1f}%."
        )
    if report_type == "performance" and "sales_performance" in payload:
        return (
            f"Overall performance metrics for the selected period. "
            f"${payload['sales_performance'].get('total_revenue', 0.0):.2f} revenue with "
            f"{payload['messaging_performance'].get('automation_rate', 0.0):.1f}% message automation."
        )
    return "Report generated successfully."


class AnalyticsService:
    """Service layer for tenant-isolated analytics, reports, and dashboard metrics."""

    def __init__(
        self,
        uow: Union[UnitOfWork, AsyncSession],
        context: Optional[TenantContext] = None,
    ):
        if isinstance(uow, UnitOfWork):
            self.uow = uow
            self.session = uow.session
        else:
            self.uow = UnitOfWork(uow)
            self.session = uow
        self.context = context

    def _resolve_context(
        self,
        context: Optional[Union[TenantContext, str, UUID]] = None,
        project_id: Optional[Union[str, UUID, TenantContext]] = None,
    ) -> TenantContext:
        if isinstance(context, (str, UUID)) and not isinstance(context, TenantContext):
            actual_project_id: Optional[Union[str, UUID]] = context
            actual_ctx = project_id if isinstance(project_id, TenantContext) else None
        else:
            actual_ctx = context
            actual_project_id = None if isinstance(project_id, TenantContext) else project_id

        ctx = _require_tenant_context(actual_ctx, self.context)
        if actual_project_id is not None and UUID(str(actual_project_id)) != ctx.project_id:
            raise PermissionError("Caller project_id does not match authenticated TenantContext")
        return ctx

    async def list_reports(
        self,
        context: Optional[Union[TenantContext, str, UUID]] = None,
        project_id: Optional[Union[str, UUID, TenantContext]] = None,
        report_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[Report]:
        """List reports strictly scoped to TenantContext."""
        ctx = self._resolve_context(context, project_id)
        async with self.uow as uow:
            repo = ReportRepository(uow.session, ctx)
            skip = (max(page, 1) - 1) * page_size
            return await repo.list_by_context(
                context=ctx, report_type=report_type, skip=skip, limit=page_size
            )

    async def get_report(
        self,
        report_id: Union[str, UUID],
        context: Optional[Union[TenantContext, str, UUID]] = None,
        project_id: Optional[Union[str, UUID, TenantContext]] = None,
    ) -> Report:
        """Retrieve a single report by ID within the active TenantContext."""
        if isinstance(context, (str, UUID)) and not isinstance(context, TenantContext):
            actual_report_id: Union[str, UUID] = context
            ctx = self._resolve_context(project_id, report_id)
        else:
            actual_report_id = report_id
            ctx = self._resolve_context(context, project_id)

        async with self.uow as uow:
            repo = ReportRepository(uow.session, ctx)
            report = await repo.get_by_context(UUID(str(actual_report_id)), context=ctx)
            if not report:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
            return report

    async def generate_project_report(
        self,
        report_type: str,
        start_date: datetime,
        end_date: datetime,
        context: Optional[TenantContext] = None,
        project_id: Optional[Union[str, UUID]] = None,
    ) -> Report:
        """Generate and persist an analytics report scoped to TenantContext."""
        ctx = self._resolve_context(context, project_id)
        if start_date > end_date:
            raise ValueError("start_date must not be after end_date")

        payload = await generate_report_service(
            db=self.session,
            project_id=ctx.project_id,
            report_type=report_type,
            date_range="custom",
            start_date=start_date,
            end_date=end_date,
            context=ctx,
        )
        summary = generate_report_summary(report_type, payload)
        repo = ReportRepository(self.session, ctx)
        return await repo.create_report(
            report_type=report_type,
            payload=payload,
            summary=summary,
            start_date=start_date,
            end_date=end_date,
            context=ctx,
        )

    async def get_dashboard_summary(
        self,
        context: Optional[Union[TenantContext, str, UUID]] = None,
        project_id: Optional[Union[str, UUID, TenantContext]] = None,
    ) -> Dict[str, Any]:
        """Compute tenant-scoped dashboard summary and fetch tenant-owned social metrics."""
        ctx = self._resolve_context(context, project_id)
        repo = ReportRepository(self.session, ctx)

        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        this_week_start = today_start - timedelta(days=today_start.weekday())
        last_week_start = this_week_start - timedelta(days=7)
        this_month_start = today_start.replace(day=1)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        tomorrow = now + timedelta(days=1)

        stats: Dict[str, Any] = {
            "today": await repo.get_period_summary_stats(today_start, tomorrow, context=ctx),
            "yesterday": await repo.get_period_summary_stats(yesterday_start, today_start, context=ctx),
            "this_week": await repo.get_period_summary_stats(this_week_start, tomorrow, context=ctx),
            "last_week": await repo.get_period_summary_stats(last_week_start, this_week_start, context=ctx),
            "this_month": await repo.get_period_summary_stats(this_month_start, tomorrow, context=ctx),
            "last_month": await repo.get_period_summary_stats(last_month_start, this_month_start, context=ctx),
        }

        try:
            integrations = await repo.get_tenant_integrations(context=ctx)
            meta_stats: Dict[str, Any] = {}
            fb_cls = FacebookClient if FacebookClient is not _fb_module.FacebookClient else _fb_module.FacebookClient
            ig_cls = InstagramClient if InstagramClient is not _ig_module.InstagramClient else _ig_module.InstagramClient

            for integration in integrations:
                if integration.project_id != ctx.project_id:
                    raise PermissionError("Cross-tenant integration access denied")
                try:
                    client_config = dict(integration.config or {})
                    if not client_config.get("access_token") and integration.extra_data:
                        ext_token = integration.extra_data.get("access_token")
                        if ext_token:
                            try:
                                from app.core.security import decrypt_pii
                                client_config["access_token"] = decrypt_pii(ext_token)
                            except Exception:
                                client_config["access_token"] = ext_token
                    for k, v in (integration.extra_data or {}).items():
                        if k not in client_config and k != "access_token":
                            client_config[k] = v

                    if integration.provider == "facebook":
                        fb_data = await fb_cls(client_config).get_page_engagement()
                        if fb_data:
                            meta_stats["facebook"] = {
                                "name": fb_data.get("name"),
                                "followers": fb_data.get("followers_count"),
                                "fans": fb_data.get("fan_count"),
                            }
                    elif integration.provider == "instagram":
                        ig_data = await ig_cls(client_config).get_instagram_engagement()
                        if ig_data:
                            meta_stats["instagram"] = {
                                "name": ig_data.get("name"),
                                "username": ig_data.get("username"),
                                "followers": ig_data.get("followers_count"),
                                "media_count": ig_data.get("media_count"),
                            }
                except Exception as provider_exc:
                    logger.error("Failed to fetch provider engagement", provider=integration.provider, error=str(provider_exc))
            if meta_stats:
                stats["social_engagement"] = meta_stats
        except PermissionError:
            raise
        except Exception as exc:
            logger.error("Failed to fetch social engagement for dashboard", error=str(exc))

        return stats
