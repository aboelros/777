"""
Report generation and analytics endpoints with AI-powered insights.
"""

from typing import List, Any, Dict, Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.db.models import Project, Report, Order, Message, MessageDirection
from app.models.schemas import ReportGenerate, ReportResponse
from app.services.report_generator import generate_report as generate_report_service

router = APIRouter()
logger = structlog.get_logger(__name__)


async def verify_project_access(project_id: UUID, user_id: str, db: AsyncSession) -> Project:
    """Helper to verify user has access to project."""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.owner_id == UUID(user_id))
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    return project


@router.post("/{project_id}/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    project_id: UUID,
    report_data: ReportGenerate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Generate a comprehensive analytics report with AI-powered insights.
    
    Report types:
    - **sales**: Sales performance and revenue analytics with AI insights
    - **orders**: Order tracking and fulfillment analytics  
    - **customers**: Customer engagement and sentiment analysis
    - **performance**: System performance and AI automation metrics
    - **roi**: Return on investment for AI automation
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    # Calculate date range
    days_diff = (report_data.end_date - report_data.start_date).days
    if days_diff <= 7:
        date_range = "last_7_days"
    elif days_diff <= 30:
        date_range = "last_30_days"
    else:
        date_range = "custom"
    
    # Generate report using comprehensive service
    try:
        payload = await generate_report_service(
            db=db,
            project_id=project_id,
            report_type=report_data.report_type,
            date_range=date_range,
            start_date=report_data.start_date,
            end_date=report_data.end_date
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Create report record
    new_report = Report(
        project_id=project_id,
        report_type=report_data.report_type,
        payload=payload,
        summary=_generate_summary(report_data.report_type, payload),
        start_date=report_data.start_date,
        end_date=report_data.end_date
    )
    
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    
    logger.info(
        "Report generated with AI insights",
        report_id=str(new_report.id),
        project_id=str(project_id),
        report_type=report_data.report_type
    )
    
    return new_report


@router.get("/{project_id}", response_model=List[ReportResponse])
async def list_reports(
    project_id: UUID,
    report_type: str = Query(None, description="Filter by report type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List all generated reports for a project.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    query = select(Report).where(Report.project_id == project_id)
    
    if report_type:
        query = query.where(Report.report_type == report_type)
    
    query = query.order_by(Report.generated_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return reports


@router.get("/{project_id}/dashboard-summary", response_model=Dict[str, Any])
async def get_dashboard_summary(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get comprehensive dashboard summary with comparisons.
    (Today vs Yesterday, This Week vs Last Week, etc.)
    """
    await verify_project_access(project_id, user_id, db)
    
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    
    this_week_start = today_start - timedelta(days=today_start.weekday())
    last_week_start = this_week_start - timedelta(days=7)
    
    this_month_start = today_start.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # Helper to get stats for a range
    async def get_stats(start, end):
        # Sales
        orders_result = await db.execute(
            select(func.count(Order.id), func.sum(Order.total))
            .where(Order.project_id == project_id)
            .where(Order.order_date >= start)
            .where(Order.order_date < end)
        )
        order_count, revenue = orders_result.first()
        
        # Messages
        msgs_result = await db.execute(
            select(func.count(Message.id))
            .where(Message.project_id == project_id)
            .where(Message.created_at >= start)
            .where(Message.created_at < end)
        )
        msg_count = msgs_result.scalar() or 0
        
        # Escalations
        escalation_result = await db.execute(
            select(func.count(Message.id))
            .where(Message.project_id == project_id)
            .where(Message.created_at >= start)
            .where(Message.created_at < end)
            .where(Message.extra_data.contains({"is_escalation": True}))
        )
        escalation_count = escalation_result.scalar() or 0
        
        return {
            "orders": order_count or 0,
            "revenue": float(revenue or 0),
            "messages": msg_count,
            "escalations": escalation_count
        }

    stats = {
        "today": await get_stats(today_start, now + timedelta(days=1)),
        "yesterday": await get_stats(yesterday_start, today_start),
        "this_week": await get_stats(this_week_start, now + timedelta(days=1)),
        "last_week": await get_stats(last_week_start, this_week_start),
        "this_month": await get_stats(this_month_start, now + timedelta(days=1)),
        "last_month": await get_stats(last_month_start, this_month_start)
    }

    # NEW: Include Meta engagement metrics
    try:
        from app.db.models import Integration
        result = await db.execute(
            select(Integration).where(Integration.project_id == project_id)
        )
        integrations = result.scalars().all()
        
        meta_stats = {}
        for integration in integrations:
            if integration.provider == "facebook":
                from app.services.integrations.facebook import FacebookClient
                client = FacebookClient(integration.extra_data or {})
                fb_data = await client.get_page_engagement()
                if fb_data:
                    meta_stats["facebook"] = {
                        "name": fb_data.get("name"),
                        "followers": fb_data.get("followers_count"),
                        "fans": fb_data.get("fan_count")
                    }
            elif integration.provider == "instagram":
                from app.services.integrations.instagram import InstagramClient
                client = InstagramClient(integration.extra_data or {})
                ig_data = await client.get_instagram_engagement()
                if ig_data:
                    meta_stats["instagram"] = {
                        "name": ig_data.get("name"),
                        "username": ig_data.get("username"),
                        "followers": ig_data.get("followers_count"),
                        "media_count": ig_data.get("media_count")
                    }
        
        if meta_stats:
            stats["social_engagement"] = meta_stats
            
    except Exception as e:
        logger.error("Failed to fetch social engagement for dashboard", error=str(e))

    return stats


@router.get("/{project_id}/{report_id}", response_model=ReportResponse)
async def get_report(
    project_id: UUID,
    report_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a specific report by ID.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(Report)
        .where(Report.id == report_id)
        .where(Report.project_id == project_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report


    return None



# ============================================================================
# Report Generation Helpers
# ============================================================================

async def _generate_sales_report(
    project_id: UUID,
    start_date: datetime,
    end_date: datetime,
    db: AsyncSession
) -> dict:
    """Generate sales analytics report."""
    
    # Get orders in date range
    result = await db.execute(
        select(Order)
        .where(Order.project_id == project_id)
        .where(Order.order_date >= start_date)
        .where(Order.order_date <= end_date)
    )
    orders = result.scalars().all()
    
    # Calculate metrics
    total_orders = len(orders)
    total_revenue = sum(o.total or 0 for o in orders)
    
    # Orders by status
    orders_by_status = {}
    for order in orders:
        status = order.status or "unknown"
        orders_by_status[status] = orders_by_status.get(status, 0) + 1
    
    # Orders by day
    orders_by_day = {}
    for order in orders:
        day = order.order_date.date().isoformat()
        if day not in orders_by_day:
            orders_by_day[day] = {"count": 0, "revenue": 0}
        orders_by_day[day]["count"] += 1
        orders_by_day[day]["revenue"] += order.total or 0
    
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "summary": {
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "average_order_value": float(total_revenue / total_orders) if total_orders > 0 else 0,
            "orders_by_status": orders_by_status
        },
        "timeline": orders_by_day
    }


async def _generate_messages_report(
    project_id: UUID,
    start_date: datetime,
    end_date: datetime,
    db: AsyncSession
) -> dict:
    """Generate messaging analytics report."""
    
    result = await db.execute(
        select(Message)
        .where(Message.project_id == project_id)
        .where(Message.created_at >= start_date)
        .where(Message.created_at <= end_date)
    )
    messages = result.scalars().all()
    
    total_messages = len(messages)
    inbound = sum(1 for m in messages if m.direction == MessageDirection.INBOUND)
    outbound = sum(1 for m in messages if m.direction == MessageDirection.OUTBOUND)
    ai_generated = sum(1 for m in messages if m.ai_generated)
    
    # Messages by provider
    by_provider = {}
    for msg in messages:
        provider = msg.provider
        if provider not in by_provider:
            by_provider[provider] = {"total": 0, "inbound": 0, "outbound": 0, "ai_generated": 0}
        by_provider[provider]["total"] += 1
        if msg.direction == MessageDirection.INBOUND:
            by_provider[provider]["inbound"] += 1
        else:
            by_provider[provider]["outbound"] += 1
        if msg.ai_generated:
            by_provider[provider]["ai_generated"] += 1
    
    # AI costs
    total_ai_cost = sum(m.ai_cost or 0 for m in messages)
    total_tokens = sum(
        (m.ai_prompt_tokens or 0) + (m.ai_completion_tokens or 0) 
        for m in messages
    )
    
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "summary": {
            "total_messages": total_messages,
            "inbound_messages": inbound,
            "outbound_messages": outbound,
            "ai_generated_messages": ai_generated,
            "automation_rate": (ai_generated / outbound * 100) if outbound > 0 else 0
        },
        "by_provider": by_provider,
        "ai_usage": {
            "total_tokens": total_tokens,
            "total_cost_usd": float(total_ai_cost),
            "average_cost_per_message": float(total_ai_cost / ai_generated) if ai_generated > 0 else 0
        }
    }


async def _generate_performance_report(
    project_id: UUID,
    start_date: datetime,
    end_date: datetime,
    db: AsyncSession
) -> dict:
    """Generate overall performance report."""
    
    # Get sales data
    sales_data = await _generate_sales_report(project_id, start_date, end_date, db)
    
    # Get messaging data
    messages_data = await _generate_messages_report(project_id, start_date, end_date, db)
    
    # Combine into performance overview
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "sales_performance": sales_data["summary"],
        "messaging_performance": messages_data["summary"],
        "ai_performance": messages_data["ai_usage"],
        "efficiency_metrics": {
            "revenue_per_message": (
                sales_data["summary"]["total_revenue"] / messages_data["summary"]["total_messages"]
                if messages_data["summary"]["total_messages"] > 0 else 0
            ),
            "ai_cost_per_order": (
                messages_data["ai_usage"]["total_cost_usd"] / sales_data["summary"]["total_orders"]
                if sales_data["summary"]["total_orders"] > 0 else 0
            )
        }
    }


def _generate_summary(report_type: str, payload: dict) -> str:
    """Generate human-readable summary from report data."""
    
    if report_type == "sales":
        summary = payload["summary"]
        return (
            f"Generated {summary['total_orders']} orders with "
            f"${summary['total_revenue']:.2f} in total revenue. "
            f"Average order value: ${summary['average_order_value']:.2f}."
        )
    
    elif report_type == "messages":
        summary = payload["summary"]
        return (
            f"Processed {summary['total_messages']} messages "
            f"({summary['inbound_messages']} inbound, {summary['outbound_messages']} outbound). "
            f"AI automation rate: {summary['automation_rate']:.1f}%."
        )
    
    elif report_type == "performance":
        return (
            f"Overall performance metrics for the selected period. "
            f"${payload['sales_performance']['total_revenue']:.2f} revenue with "
            f"{payload['messaging_performance']['automation_rate']:.1f}% message automation."
        )
    
    return "Report generated successfully."
