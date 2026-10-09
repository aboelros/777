from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import TenantContext
from app.core.repository import BaseRepository
from app.domains.analytics.models import APILog, Report
from app.domains.integrations.models import Integration
from app.domains.integrations.repository import IntegrationRepository
from app.domains.messages.models import Message
from app.domains.orders.models import Order


def _require_tenant_context(
    context: Optional[TenantContext],
    bound_context: Optional[TenantContext] = None,
) -> TenantContext:
    """Validate and return an active TenantContext or fail closed."""
    ctx = context or bound_context
    if not ctx or not isinstance(ctx, TenantContext) or not ctx.project_id:
        raise PermissionError("Valid TenantContext is required for analytics repository access")
    return ctx


class ReportRepository(BaseRepository[Report]):
    """Tenant-scoped repository for analytics reports and aggregated project metrics."""

    def __init__(self, session: AsyncSession, context: Optional[TenantContext] = None):
        super().__init__(Report, session)
        self.context = context

    def _get_context(self, context: Optional[TenantContext] = None) -> TenantContext:
        return _require_tenant_context(context, self.context)

    async def get(self, id: Any, context: Optional[TenantContext] = None) -> Optional[Report]:
        """Override BaseRepository.get to fail closed without TenantContext."""
        return await self.get_by_context(UUID(str(id)), context=context)

    async def get_by_context(
        self,
        report_id: UUID,
        context: Optional[TenantContext] = None,
    ) -> Optional[Report]:
        """Fetch a single report strictly scoped to TenantContext at the SQL level."""
        ctx = self._get_context(context)
        query = select(self.model).where(
            self.model.id == report_id,
            self.model.project_id == ctx.project_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_context(
        self,
        context: Optional[TenantContext] = None,
        report_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Report]:
        """List reports belonging to the active TenantContext."""
        ctx = self._get_context(context)
        query = select(self.model).where(self.model.project_id == ctx.project_id)
        if report_type:
            query = query.where(self.model.report_type == report_type)
        query = query.order_by(desc(self.model.generated_at)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_project(
        self,
        project_id: UUID,
        context: Optional[TenantContext] = None,
    ) -> List[Report]:
        """Fetch reports for project_id after reconciling with TenantContext."""
        ctx = self._get_context(context)
        if UUID(str(project_id)) != ctx.project_id:
            raise PermissionError("Caller project_id does not match authenticated TenantContext")
        return await self.list_by_context(context=ctx, limit=100)

    async def create_report(
        self,
        report_type: str,
        payload: Dict[str, Any],
        summary: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        context: Optional[TenantContext] = None,
    ) -> Report:
        """Persist a new Report bound strictly to context.project_id."""
        ctx = self._get_context(context)
        new_report = Report(
            project_id=ctx.project_id,
            report_type=report_type,
            payload=payload,
            summary=summary,
            start_date=start_date,
            end_date=end_date,
        )
        self.session.add(new_report)
        await self.session.commit()
        await self.session.refresh(new_report)
        return new_report

    async def get_range_orders(
        self,
        start_date: datetime,
        end_date: datetime,
        context: Optional[TenantContext] = None,
        desc_order: bool = False,
    ) -> List[Order]:
        """Fetch tenant-owned orders within a date range."""
        ctx = self._get_context(context)
        query = select(Order).where(
            and_(
                Order.project_id == ctx.project_id,
                Order.order_date >= start_date,
                Order.order_date <= end_date,
            )
        )
        if desc_order:
            query = query.order_by(Order.order_date.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_range_messages(
        self,
        start_date: datetime,
        end_date: datetime,
        context: Optional[TenantContext] = None,
    ) -> List[Message]:
        """Fetch tenant-owned messages within a date range."""
        ctx = self._get_context(context)
        query = select(Message).where(
            and_(
                Message.project_id == ctx.project_id,
                Message.created_at >= start_date,
                Message.created_at <= end_date,
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_period_summary_stats(
        self,
        start_date: datetime,
        end_date: datetime,
        context: Optional[TenantContext] = None,
    ) -> Dict[str, Any]:
        """Compute tenant-scoped order, revenue, message, and escalation aggregates."""
        ctx = self._get_context(context)
        orders_result = await self.session.execute(
            select(func.count(Order.id), func.sum(Order.total))
            .where(Order.project_id == ctx.project_id)
            .where(Order.order_date >= start_date)
            .where(Order.order_date < end_date)
        )
        order_count, revenue = orders_result.first()

        msgs_result = await self.session.execute(
            select(func.count(Message.id))
            .where(Message.project_id == ctx.project_id)
            .where(Message.created_at >= start_date)
            .where(Message.created_at < end_date)
        )
        msg_count = msgs_result.scalar() or 0

        escalation_result = await self.session.execute(
            select(func.count(Message.id))
            .where(Message.project_id == ctx.project_id)
            .where(Message.created_at >= start_date)
            .where(Message.created_at < end_date)
            .where(Message.extra_data.contains({"is_escalation": True}))
        )
        escalation_count = escalation_result.scalar() or 0

        return {
            "orders": order_count or 0,
            "revenue": float(revenue or 0),
            "messages": msg_count,
            "escalations": escalation_count,
        }

    async def get_tenant_integrations(
        self,
        context: Optional[TenantContext] = None,
    ) -> List[Integration]:
        """Retrieve integrations strictly scoped to the active TenantContext."""
        ctx = self._get_context(context)
        integration_repo = IntegrationRepository(self.session)
        integrations = await integration_repo.get_project_integrations(ctx.project_id)
        return [i for i in integrations if i.project_id == ctx.project_id]


class APILogRepository(BaseRepository[APILog]):
    """Tenant-scoped repository for API usage logs."""

    def __init__(self, session: AsyncSession, context: Optional[TenantContext] = None):
        super().__init__(APILog, session)
        self.context = context

    def _get_context(self, context: Optional[TenantContext] = None) -> TenantContext:
        return _require_tenant_context(context, self.context)

    async def get(self, id: Any, context: Optional[TenantContext] = None) -> Optional[APILog]:
        """Override BaseRepository.get to fail closed without TenantContext."""
        return await self.get_by_context(int(id), context=context)

    async def get_by_context(
        self,
        log_id: int,
        context: Optional[TenantContext] = None,
    ) -> Optional[APILog]:
        ctx = self._get_context(context)
        query = select(self.model).where(
            self.model.id == log_id,
            self.model.project_id == ctx.project_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_context(
        self,
        context: Optional[TenantContext] = None,
        limit: int = 100,
    ) -> List[APILog]:
        ctx = self._get_context(context)
        query = (
            select(self.model)
            .where(self.model.project_id == ctx.project_id)
            .order_by(desc(self.model.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_project(
        self,
        project_id: UUID,
        context: Optional[TenantContext] = None,
    ) -> List[APILog]:
        ctx = self._get_context(context)
        if UUID(str(project_id)) != ctx.project_id:
            raise PermissionError("Caller project_id does not match authenticated TenantContext")
        return await self.list_by_context(context=ctx)
