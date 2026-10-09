"""
Report generation and analytics endpoints with AI-powered insights.
Enforces TenantContext across all routes before any repository query or external call.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.api.dependencies.tenant import get_tenant_context
from app.core.context import TenantContext
from app.core.database import get_db
from app.core.uow import UnitOfWork
from app.domains.analytics.schemas import ReportGenerate, ReportResponse
from app.domains.analytics.service import (
    AnalyticsService,
    generate_report_summary as _generate_summary,
)

router = APIRouter()
logger = structlog.get_logger(__name__)


def _reconcile_tenant_project(project_id: UUID, context: TenantContext) -> None:
    """Verify route project_id matches authenticated TenantContext before any side effect."""
    if not context or not isinstance(context, TenantContext) or not context.project_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Valid TenantContext is required",
        )
    if project_id != context.project_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-tenant project access denied",
        )


async def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    """Dependency providing a UnitOfWork-backed AnalyticsService."""
    return AnalyticsService(UnitOfWork(db))


@router.post(
    "/{project_id}/generate",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_report(
    project_id: UUID,
    report_data: ReportGenerate,
    context: TenantContext = Depends(get_tenant_context),
    service: AnalyticsService = Depends(get_analytics_service),
) -> Any:
    """
    Generate a comprehensive analytics report with AI-powered insights.
    Strictly scoped to the authenticated TenantContext.
    """
    _reconcile_tenant_project(project_id, context)

    try:
        new_report = await service.generate_project_report(
            report_type=report_data.report_type,
            start_date=report_data.start_date,
            end_date=report_data.end_date,
            context=context,
            project_id=project_id,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    logger.info(
        "Report generated with AI insights",
        report_id=str(new_report.id),
        project_id=str(context.project_id),
        report_type=report_data.report_type,
    )
    return new_report


@router.get("/{project_id}", response_model=List[ReportResponse])
async def list_reports(
    project_id: UUID,
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    context: TenantContext = Depends(get_tenant_context),
    service: AnalyticsService = Depends(get_analytics_service),
) -> Any:
    """List all generated reports for the authenticated tenant project."""
    _reconcile_tenant_project(project_id, context)
    try:
        return await service.list_reports(
            context=context,
            project_id=project_id,
            report_type=report_type,
            page=page,
            page_size=page_size,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get("/{project_id}/dashboard-summary", response_model=Dict[str, Any])
async def get_dashboard_summary(
    project_id: UUID,
    context: TenantContext = Depends(get_tenant_context),
    service: AnalyticsService = Depends(get_analytics_service),
) -> Any:
    """
    Get comprehensive tenant-scoped dashboard summary with period comparisons
    and tenant-owned Meta engagement metrics.
    """
    _reconcile_tenant_project(project_id, context)
    try:
        return await service.get_dashboard_summary(
            context=context,
            project_id=project_id,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get("/{project_id}/{report_id}", response_model=ReportResponse)
async def get_report(
    project_id: UUID,
    report_id: UUID,
    context: TenantContext = Depends(get_tenant_context),
    service: AnalyticsService = Depends(get_analytics_service),
) -> Any:
    """Get a specific report by ID strictly within the authenticated TenantContext."""
    _reconcile_tenant_project(project_id, context)
    try:
        return await service.get_report(
            report_id=report_id,
            context=context,
            project_id=project_id,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
