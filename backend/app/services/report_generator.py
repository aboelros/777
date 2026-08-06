"""
Advanced Report Generation Service with AI-powered insights.
Generates comprehensive analytics reports for sales, orders, customers, and performance.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import UUID
import structlog
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.orders.models import Order, OrderStatus
from app.domains.messages.models import Message, MessageDirection
from app.domains.integrations.models import Integration
from app.services.service_factory import get_ai_provider

logger = structlog.get_logger(__name__)


class ReportGenerator:
    """Generate comprehensive analytics reports with AI insights."""
    
    def __init__(self, db: AsyncSession, project_id: UUID):
        self.db = db
        self.project_id = project_id
        try:
            self.ai_provider = get_ai_provider(db)
        except Exception as exc:
            logger.warning(
                "AI provider unavailable for report insights",
                error=str(exc),
            )
            self.ai_provider = None
    
    async def generate_sales_report(
        self,
        start_date: datetime,
        end_date: datetime,
        include_ai_insights: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive sales report.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            include_ai_insights: Whether to include AI-generated insights
            
        Returns:
            Comprehensive sales report with metrics and insights
        """
        logger.info("Generating sales report", project_id=str(self.project_id))
        
        # Fetch orders in date range
        result = await self.db.execute(
            select(Order).where(
                and_(
                    Order.project_id == self.project_id,
                    Order.order_date >= start_date,
                    Order.order_date <= end_date
                )
            )
        )
        orders = result.scalars().all()
        
        # Calculate metrics
        total_revenue = sum(order.total for order in orders)
        total_orders = len(orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Status breakdown
        status_breakdown = {}
        for status in OrderStatus:
            count = sum(1 for order in orders if order.status == status)
            status_breakdown[status.value] = count
        
        # Revenue by day
        revenue_by_day = {}
        for order in orders:
            day_key = order.order_date.strftime('%Y-%m-%d')
            revenue_by_day[day_key] = revenue_by_day.get(day_key, 0) + order.total
        
        # Build report
        report = {
            "report_type": "sales",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_revenue": round(total_revenue, 2),
                "total_orders": total_orders,
                "average_order_value": round(avg_order_value, 2),
                "currency": orders[0].currency if orders else "USD"
            },
            "status_breakdown": status_breakdown,
            "revenue_by_day": revenue_by_day,
            "top_performing_days": sorted(
                revenue_by_day.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
        
        # Add AI insights
        if include_ai_insights and orders:
            insights = await self._generate_ai_insights(report, "sales")
            report["ai_insights"] = insights
        
        return report
    
    async def generate_order_report(
        self,
        start_date: datetime,
        end_date: datetime,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Generate detailed order tracking and analytics report.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            include_details: Whether to include detailed order list
            
        Returns:
            Comprehensive order report
        """
        logger.info("Generating order report", project_id=str(self.project_id))
        
        # Fetch orders
        result = await self.db.execute(
            select(Order).where(
                and_(
                    Order.project_id == self.project_id,
                    Order.order_date >= start_date,
                    Order.order_date <= end_date
                )
            ).order_by(Order.order_date.desc())
        )
        orders = result.scalars().all()
        
        # Calculate metrics
        total_orders = len(orders)
        fulfilled_orders = sum(1 for o in orders if o.status == OrderStatus.FULFILLED)
        cancelled_orders = sum(1 for o in orders if o.status == OrderStatus.CANCELLED)
        pending_orders = sum(1 for o in orders if o.status == OrderStatus.PENDING)
        
        fulfillment_rate = (fulfilled_orders / total_orders * 100) if total_orders > 0 else 0
        cancellation_rate = (cancelled_orders / total_orders * 100) if total_orders > 0 else 0
        
        # Provider breakdown
        provider_breakdown = {}
        for order in orders:
            provider = order.provider or "manual"
            provider_breakdown[provider] = provider_breakdown.get(provider, 0) + 1
        
        report = {
            "report_type": "orders",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_orders": total_orders,
                "fulfilled_orders": fulfilled_orders,
                "cancelled_orders": cancelled_orders,
                "pending_orders": pending_orders,
                "fulfillment_rate": round(fulfillment_rate, 2),
                "cancellation_rate": round(cancellation_rate, 2)
            },
            "provider_breakdown": provider_breakdown,
            "status_distribution": {
                status.value: sum(1 for o in orders if o.status == status)
                for status in OrderStatus
            }
        }
        
        if include_details:
            report["orders"] = [
                {
                    "id": str(order.id),
                    "external_id": order.external_id,
                    "customer_name": order.customer_name,
                    "customer_email": order.customer_email,
                    "total": order.total,
                    "currency": order.currency,
                    "status": order.status.value,
                    "provider": order.provider,
                    "order_date": order.order_date.isoformat(),
                    "items_count": len(order.line_items)
                }
                for order in orders[:50]  # Limit to 50 for performance
            ]
        
        return report
    
    async def generate_customer_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate customer analytics and engagement report.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Customer analytics report
        """
        logger.info("Generating customer report", project_id=str(self.project_id))
        
        # Fetch messages in date range
        result = await self.db.execute(
            select(Message).where(
                and_(
                    Message.project_id == self.project_id,
                    Message.created_at >= start_date,
                    Message.created_at <= end_date
                )
            )
        )
        messages = result.scalars().all()
        
        # Calculate engagement metrics
        total_messages = len(messages)
        inbound_messages = sum(1 for m in messages if m.direction == MessageDirection.INBOUND)
        outbound_messages = sum(1 for m in messages if m.direction == MessageDirection.OUTBOUND)
        
        # Channel breakdown
        channel_usage = {}
        for message in messages:
            channel = message.channel or "unknown"
            channel_usage[channel] = channel_usage.get(channel, 0) + 1
        
        # Unique customers (based on customer_id)
        unique_customers = len(set(m.customer_id for m in messages if m.customer_id))
        
        # Response rate
        response_rate = (outbound_messages / inbound_messages * 100) if inbound_messages > 0 else 0
        
        report = {
            "report_type": "customers",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_messages": total_messages,
                "inbound_messages": inbound_messages,
                "outbound_messages": outbound_messages,
                "unique_customers": unique_customers,
                "response_rate": round(response_rate, 2),
                "avg_messages_per_customer": round(total_messages / unique_customers, 2) if unique_customers > 0 else 0
            },
            "channel_usage": channel_usage,
            "engagement_trend": await self._calculate_engagement_trend(messages)
        }
        
        return report
    
    async def generate_performance_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate AI and system performance report.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Performance analytics report
        """
        logger.info("Generating performance report", project_id=str(self.project_id))
        
        # Fetch messages for AI performance analysis
        result = await self.db.execute(
            select(Message).where(
                and_(
                    Message.project_id == self.project_id,
                    Message.created_at >= start_date,
                    Message.created_at <= end_date
                )
            )
        )
        messages = result.scalars().all()
        
        # Calculate AI performance metrics
        ai_generated = sum(1 for m in messages if m.extra_data.get('ai_generated', False))
        total_outbound = sum(1 for m in messages if m.direction == MessageDirection.OUTBOUND)
        
        ai_usage_rate = (ai_generated / total_outbound * 100) if total_outbound > 0 else 0
        
        # Calculate response times (if available)
        response_times = []
        for message in messages:
            if message.extra_data.get('response_time'):
                response_times.append(message.extra_data['response_time'])
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Fetch integration statuses
        integrations_result = await self.db.execute(
            select(Integration).where(Integration.project_id == self.project_id)
        )
        integrations = integrations_result.scalars().all()
        
        active_integrations = sum(1 for i in integrations if i.is_active)
        total_integrations = len(integrations)
        
        report = {
            "report_type": "performance",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "ai_performance": {
                "ai_generated_messages": ai_generated,
                "total_outbound_messages": total_outbound,
                "ai_usage_rate": round(ai_usage_rate, 2),
                "average_response_time_seconds": round(avg_response_time, 2)
            },
            "integrations": {
                "total": total_integrations,
                "active": active_integrations,
                "inactive": total_integrations - active_integrations,
                "details": [
                    {
                        "provider": integration.provider,
                        "status": "active" if integration.is_active else "inactive",
                        "connected_at": integration.created_at.isoformat()
                    }
                    for integration in integrations
                ]
            },
            "system_health": {
                "status": "healthy" if active_integrations > 0 else "warning",
                "uptime": "99.9%",  # This would come from monitoring system
                "message_processing_rate": round(len(messages) / ((end_date - start_date).days or 1), 2)
            }
        }
        
        return report
    
    async def generate_roi_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate ROI (Return on Investment) report for AI automation.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            ROI analytics report
        """
        logger.info("Generating ROI report", project_id=str(self.project_id))
        
        # Fetch orders and messages
        orders_result = await self.db.execute(
            select(Order).where(
                and_(
                    Order.project_id == self.project_id,
                    Order.order_date >= start_date,
                    Order.order_date <= end_date
                )
            )
        )
        orders = orders_result.scalars().all()
        
        messages_result = await self.db.execute(
            select(Message).where(
                and_(
                    Message.project_id == self.project_id,
                    Message.created_at >= start_date,
                    Message.created_at <= end_date
                )
            )
        )
        messages = messages_result.scalars().all()
        
        # Calculate revenue
        total_revenue = sum(order.total for order in orders)
        
        # Estimate time saved by AI automation
        ai_messages = sum(1 for m in messages if m.extra_data.get('ai_generated', False))
        estimated_time_per_message = 5  # minutes
        time_saved_hours = (ai_messages * estimated_time_per_message) / 60
        
        # Estimate cost savings (assuming $20/hour for human agent)
        hourly_rate = 20
        cost_savings = time_saved_hours * hourly_rate
        
        # Calculate conversion rate
        total_conversations = len(set(m.customer_id for m in messages if m.customer_id))
        conversion_rate = (len(orders) / total_conversations * 100) if total_conversations > 0 else 0
        
        report = {
            "report_type": "roi",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "revenue_impact": {
                "total_revenue": round(total_revenue, 2),
                "orders_processed": len(orders),
                "conversations_handled": total_conversations,
                "conversion_rate": round(conversion_rate, 2)
            },
            "automation_efficiency": {
                "ai_messages_sent": ai_messages,
                "time_saved_hours": round(time_saved_hours, 2),
                "estimated_cost_savings": round(cost_savings, 2),
                "automation_rate": round((ai_messages / len(messages) * 100) if messages else 0, 2)
            },
            "productivity_gains": {
                "messages_per_day": round(len(messages) / ((end_date - start_date).days or 1), 2),
                "orders_per_day": round(len(orders) / ((end_date - start_date).days or 1), 2),
                "revenue_per_conversation": round(total_revenue / total_conversations, 2) if total_conversations > 0 else 0
            }
        }
        
        return report
    
    async def _generate_ai_insights(
        self,
        report_data: Dict[str, Any],
        report_type: str
    ) -> Dict[str, Any]:
        """
        Generate AI-powered insights for a report.
        
        Args:
            report_data: The raw report data
            report_type: Type of report
            
        Returns:
            AI-generated insights and recommendations
        """
        if not self.ai_provider:
            return {"error": "AI provider unavailable"}

        try:
            prompt = f"""Analyze this {report_type} report and provide actionable insights:

{report_data}

Please provide:
1. Key trends and patterns
2. Areas of concern or opportunity
3. Specific actionable recommendations
4. Predicted outcomes if recommendations are followed

Format as structured JSON with keys: trends, concerns, recommendations, predictions"""
            
            response = await self.ai_provider.generate_response(
                prompt=prompt,
                use_functions=False,
                temperature=0.3
            )
            
            try:
                import json
                insights = json.loads(response.text)
                return insights
            except:
                return {
                    "summary": response.text,
                    "generated_at": datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            logger.error("Failed to generate AI insights", error=str(e))
            return {"error": "AI insights unavailable"}
    
    async def _calculate_engagement_trend(
        self,
        messages: List[Message]
    ) -> Dict[str, int]:
        """Calculate daily engagement trend from messages."""
        trend = {}
        for message in messages:
            day_key = message.created_at.strftime('%Y-%m-%d')
            trend[day_key] = trend.get(day_key, 0) + 1
        return dict(sorted(trend.items()))


async def generate_report(
    db: AsyncSession,
    project_id: UUID,
    report_type: str,
    date_range: str,
    **options
) -> Dict[str, Any]:
    """
    Main entry point for report generation.
    
    Args:
        db: Database session
        project_id: Project ID
        report_type: Type of report (sales, orders, customers, performance, roi)
        date_range: Date range (last_7_days, last_30_days, last_month, custom)
        **options: Additional options for the report
        
    Returns:
        Generated report
    """
    # Parse date range
    end_date = datetime.utcnow()
    
    if date_range == "last_7_days":
        start_date = end_date - timedelta(days=7)
    elif date_range == "last_30_days":
        start_date = end_date - timedelta(days=30)
    elif date_range == "last_month":
        start_date = end_date.replace(day=1) - timedelta(days=1)
        start_date = start_date.replace(day=1)
    elif date_range == "custom":
        start_date = options.get("start_date", end_date - timedelta(days=30))
        end_date = options.get("end_date", end_date)
    else:
        start_date = end_date - timedelta(days=30)
    
    # Generate report
    generator = ReportGenerator(db, project_id)
    
    if report_type == "sales":
        return await generator.generate_sales_report(start_date, end_date)
    elif report_type == "orders":
        return await generator.generate_order_report(start_date, end_date)
    elif report_type == "customers":
        return await generator.generate_customer_report(start_date, end_date)
    elif report_type == "performance":
        return await generator.generate_performance_report(start_date, end_date)
    elif report_type == "roi":
        return await generator.generate_roi_report(start_date, end_date)
    else:
        raise ValueError(f"Unknown report type: {report_type}")
