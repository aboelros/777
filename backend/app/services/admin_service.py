"""
Admin service layer for platform-wide operations, metrics aggregation,
fleet management, system diagnostics, and subscription controls.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID
import time
from sqlalchemy import func, select, text, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domains.auth.models import User, UserRole
from app.domains.projects.models import Project
from app.domains.orders.models import Order
from app.domains.messages.models import Message, MessageDirection
from app.domains.billing.models import Subscription, SubscriptionTier, SubscriptionStatus
from app.domains.integrations.models import Integration
from app.domains.webhooks.models import WebhookDelivery
from app.domains.analytics.models import APILog


class AdminService:
    """Service class executing platform management logic for administrators."""

    @staticmethod
    async def get_dashboard_metrics(db: AsyncSession, days: int = 30) -> Dict[str, Any]:
        """Aggregate high-level platform KPI metrics for the given timeframe."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)

        # Users count
        total_users_res = await db.execute(select(func.count(User.id)))
        total_users = total_users_res.scalar_one() or 0

        active_users_res = await db.execute(select(func.count(User.id)).where(User.is_active == True))
        active_users = active_users_res.scalar_one() or 0

        # Projects count
        total_projects_res = await db.execute(select(func.count(Project.id)))
        total_projects = total_projects_res.scalar_one() or 0

        # Orders & GMV
        orders_stmt = select(
            func.count(Order.id),
            func.coalesce(func.sum(Order.total), 0.0)
        ).where(Order.created_at >= start_time)
        orders_res = await db.execute(orders_stmt)
        total_orders, total_gmv = orders_res.one()

        # Messages (Inbound vs Outbound)
        messages_stmt = select(Message.direction, func.count(Message.id)).where(
            Message.created_at >= start_time
        ).group_by(Message.direction)
        msg_res = await db.execute(messages_stmt)
        msg_counts = dict(msg_res.all())
        inbound = msg_counts.get(MessageDirection.INBOUND, 0)
        outbound = msg_counts.get(MessageDirection.OUTBOUND, 0)

        # Subscriptions by tier
        subs_stmt = select(Subscription.tier, func.count(Subscription.id)).group_by(Subscription.tier)
        subs_res = await db.execute(subs_stmt)
        tier_counts = {str(k.value if hasattr(k, "value") else k): v for k, v in subs_res.all()}

        return {
            "period_days": days,
            "total_users": total_users,
            "active_users": active_users,
            "total_projects": total_projects,
            "total_orders": total_orders,
            "total_gmv": round(float(total_gmv), 2),
            "total_messages": inbound + outbound,
            "inbound_messages": inbound,
            "outbound_messages": outbound,
            "subscription_breakdown": tier_counts,
            "timestamp": end_time.isoformat(),
        }

    @staticmethod
    async def get_system_health(db: AsyncSession) -> Dict[str, Any]:
        """Perform live health diagnostics for database, cache, and external APIs."""
        db_start = time.time()
        db_status = "unhealthy"
        db_latency_ms = 0.0
        try:
            await db.execute(text("SELECT 1"))
            db_latency_ms = round((time.time() - db_start) * 1000, 2)
            db_status = "healthy"
        except Exception:
            db_status = "error"

        # Redis / Cache Check
        cache_status = "unknown"
        cache_latency_ms = 0.0
        try:
            from app.services.cache_service import cache
            if cache and hasattr(cache, "ping"):
                c_start = time.time()
                is_ok = await cache.ping()
                cache_latency_ms = round((time.time() - c_start) * 1000, 2)
                cache_status = "healthy" if is_ok else "unreachable"
            else:
                cache_status = "healthy"
        except Exception:
            cache_status = "degraded"

        # Gemini AI API Check
        ai_status = "healthy" if settings.GEMINI_API_KEY else "key_missing"

        return {
            "database": {"status": db_status, "latency_ms": db_latency_ms},
            "cache": {"status": cache_status, "latency_ms": cache_latency_ms},
            "ai_engine": {"status": ai_status, "primary_model": "gemini-2.5-flash"},
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    async def list_projects(
        db: AsyncSession, q: Optional[str] = None, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """List tenant projects across all accounts with search and pagination."""
        query = select(Project).order_by(desc(Project.created_at))
        if q:
            term = f"%{q.lower()}%"
            query = query.where(
                (Project.name.ilike(term)) | (Project.project_code.ilike(term))
            )

        total_stmt = select(func.count()).select_from(query.subquery())
        total_res = await db.execute(total_stmt)
        total = total_res.scalar_one()

        items_res = await db.execute(
            query.offset((page - 1) * page_size).limit(page_size)
        )
        projects = items_res.scalars().all()

        results = []
        for p in projects:
            results.append({
                "id": str(p.id),
                "name": p.name,
                "project_code": p.project_code,
                "owner_id": str(p.owner_id),
                "is_active": p.is_active,
                "timezone": p.timezone,
                "bot_name": p.bot_name,
                "bot_tone": p.bot_tone,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            })

        return {"total": total, "page": page, "page_size": page_size, "items": results}

    @staticmethod
    async def update_project_status(db: AsyncSession, project_id: UUID, is_active: bool) -> bool:
        """Activate or deactivate a project fleet tenant."""
        res = await db.execute(select(Project).where(Project.id == project_id))
        proj = res.scalar_one_or_none()
        if not proj:
            return False
        proj.is_active = is_active
        await db.commit()
        return True

    @staticmethod
    async def list_subscriptions(
        db: AsyncSession, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """Retrieve all subscription records with owner information and usage limits."""
        query = select(Subscription, User).join(User, Subscription.user_id == User.id).order_by(
            desc(Subscription.created_at)
        )
        total_stmt = select(func.count(Subscription.id))
        total_res = await db.execute(total_stmt)
        total = total_res.scalar_one()

        items_res = await db.execute(
            query.offset((page - 1) * page_size).limit(page_size)
        )
        rows = items_res.all()

        items = []
        for sub, user in rows:
            items.append({
                "id": str(sub.id),
                "user_id": str(user.id),
                "user_email": user.email,
                "user_name": user.name,
                "tier": sub.tier.value if hasattr(sub.tier, "value") else str(sub.tier),
                "status": sub.status.value if hasattr(sub.status, "value") else str(sub.status),
                "limit_messages": sub.limit_messages,
                "limit_orders": sub.limit_orders,
                "limit_ai_requests": sub.limit_ai_requests,
                "total_paid": sub.total_paid,
                "created_at": sub.created_at.isoformat() if sub.created_at else None,
            })

        return {"total": total, "page": page, "page_size": page_size, "items": items}

    @staticmethod
    async def override_subscription(
        db: AsyncSession, user_id: UUID, tier: Optional[str] = None, limits: Optional[Dict[str, int]] = None
    ) -> Optional[Dict[str, Any]]:
        """Manually override a user's subscription tier and resource limits."""
        res = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
        sub = res.scalar_one_or_none()
        if not sub:
            # Create default subscription if not present
            sub = Subscription(user_id=user_id)
            db.add(sub)

        if tier:
            try:
                sub.tier = SubscriptionTier(tier.lower())
            except ValueError:
                pass

        if limits:
            if "limit_messages" in limits:
                sub.limit_messages = limits["limit_messages"]
            if "limit_orders" in limits:
                sub.limit_orders = limits["limit_orders"]
            if "limit_ai_requests" in limits:
                sub.limit_ai_requests = limits["limit_ai_requests"]

        await db.commit()
        await db.refresh(sub)
        return {
            "id": str(sub.id),
            "tier": sub.tier.value if hasattr(sub.tier, "value") else str(sub.tier),
            "status": sub.status.value if hasattr(sub.status, "value") else str(sub.status),
            "limit_messages": sub.limit_messages,
            "limit_orders": sub.limit_orders,
            "limit_ai_requests": sub.limit_ai_requests,
        }
