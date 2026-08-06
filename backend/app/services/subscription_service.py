"""
Subscription Management Service.
Handles subscriptions, usage tracking, and limit enforcement.
"""

from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
import structlog

from app.domains.auth.models import User
from app.domains.billing.models import Subscription, UsageTracking, SubscriptionTier, SubscriptionStatus
from app.domains.messages.models import Message
from app.domains.orders.models import Order
from app.domains.projects.models import Project
from app.core.subscription_plans import (
    TIER_LIMITS, TIER_PRICING, 
    get_tier_info, check_limit, check_feature_access
)

logger = structlog.get_logger(__name__)


class SubscriptionService:
    """Manage user subscriptions and usage."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def _get_user_tier(self, user: User) -> SubscriptionTier:
        """Get user's subscription tier from Subscription relationship."""
        if not user:
            return SubscriptionTier.FREE
        
        # Query subscription directly to avoid lazy load issues with greenlet
        # Do NOT access user.subscription here as it triggers sync lazy load
        result = await self.db.execute(
            select(Subscription).where(Subscription.user_id == user.id)
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            return subscription.tier
        
        # Default to FREE if no subscription
        return SubscriptionTier.FREE
    
    async def get_user_subscription(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get user's current subscription details."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Get subscription record
        result = await self.db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()
        
        # Get tier info
        tier = await self._get_user_tier(user)
        tier_info = get_tier_info(tier)
        
        # Get current usage
        usage = await self.get_current_usage(user_id)
        
        return {
            "user_id": str(user.id),
            "email": user.email,
            "tier": tier.value,
            "status": subscription.status.value if subscription else "active",
            "tier_info": tier_info,
            "subscription": {
                "started_at": subscription.started_at.isoformat() if subscription and subscription.started_at else None,
                "expires_at": subscription.expires_at.isoformat() if subscription and subscription.expires_at else None,
                "next_billing_date": subscription.next_billing_date.isoformat() if subscription and subscription.next_billing_date else None,
                "billing_cycle": subscription.billing_cycle if subscription else "monthly",
                "total_paid": subscription.total_paid if subscription else 0.0
            } if subscription else None,
            "usage": usage,
            "limits_status": await self.check_all_limits(user_id)
        }
    
    async def create_subscription(
        self,
        user_id: UUID,
        tier: SubscriptionTier,
        billing_cycle: str = "monthly"
    ) -> Dict[str, Any]:
        """Create or update user subscription."""
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Get tier pricing
        pricing = TIER_PRICING[tier]
        limits = TIER_LIMITS[tier]
        
        price = pricing["monthly_price"] if billing_cycle == "monthly" else pricing["annual_price"]
        
        # Check if subscription exists
        result = await self.db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()
        
        now = datetime.utcnow()
        
        if subscription:
            # Update existing
            subscription.tier = tier
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.billing_cycle = billing_cycle
            subscription.price_monthly = pricing["monthly_price"]
            subscription.price_annually = pricing["annual_price"]
            
            # Update limits
            subscription.limit_messages = limits["messages"]
            subscription.limit_orders = limits["orders"]
            subscription.limit_ai_requests = limits["ai_requests"]
            subscription.limit_projects = limits["projects"]
            subscription.limit_integrations = limits["integrations"]
            subscription.limit_storage_gb = limits["storage_gb"]
            subscription.limit_team_members = limits["team_members"]
            
            # Update features
            subscription.features = {
                "ai_automation": limits["ai_automation"],
                "advanced_reports": limits["advanced_reports"],
                "social_media_management": limits["social_media_management"],
                "conversation_memory": limits["conversation_memory"],
                "order_automation": limits["order_automation"],
                "api_access": limits["api_access"],
                "white_label": limits["white_label"],
                "custom_ai": limits["custom_ai"]
            }
            
            # Set billing dates
            if billing_cycle == "monthly":
                subscription.next_billing_date = now + timedelta(days=30)
            else:
                subscription.next_billing_date = now + timedelta(days=365)
            
        else:
            # Create new subscription
            subscription = Subscription(
                user_id=user_id,
                tier=tier,
                status=SubscriptionStatus.ACTIVE,
                billing_cycle=billing_cycle,
                price_monthly=pricing["monthly_price"],
                price_annually=pricing["annual_price"],
                started_at=now,
                expires_at=now + timedelta(days=30 if billing_cycle == "monthly" else 365),
                next_billing_date=now + timedelta(days=30 if billing_cycle == "monthly" else 365),
                limit_messages=limits["messages"],
                limit_orders=limits["orders"],
                limit_ai_requests=limits["ai_requests"],
                limit_projects=limits["projects"],
                limit_integrations=limits["integrations"],
                limit_storage_gb=limits["storage_gb"],
                limit_team_members=limits["team_members"],
                features={
                    "ai_automation": limits["ai_automation"],
                    "advanced_reports": limits["advanced_reports"],
                    "social_media_management": limits["social_media_management"],
                    "conversation_memory": limits["conversation_memory"],
                    "order_automation": limits["order_automation"],
                    "api_access": limits["api_access"],
                    "white_label": limits["white_label"],
                    "custom_ai": limits["custom_ai"]
                }
            )
            self.db.add(subscription)
        
        # Note: Tier is now stored in Subscription model, not User
        # user.subscription_tier and user.subscription_status removed from User model
        user.subscription_started_at = subscription.started_at
        user.subscription_expires_at = subscription.expires_at
        
        await self.db.commit()
        await self.db.refresh(subscription)
        
        logger.info(
            "Subscription created/updated",
            user_id=str(user_id),
            tier=tier.value,
            price=price
        )
        
        return {
            "subscription_id": str(subscription.id),
            "tier": tier.value,
            "status": SubscriptionStatus.ACTIVE.value,
            "billing_cycle": billing_cycle,
            "price": price,
            "next_billing_date": subscription.next_billing_date.isoformat()
        }
    
    async def get_current_usage(self, user_id: UUID) -> Dict[str, int]:
        """Get current month usage for user."""
        from app.domains.messages.models import Message
        from app.domains.orders.models import Order
        from app.domains.projects.models import Project
        
        # Get current month start
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Count messages
        result = await self.db.execute(
            select(func.count(Message.id))
            .join(Project, Message.project_id == Project.id)
            .where(
                and_(
                    Project.owner_id == user_id,
                    Message.created_at >= month_start
                )
            )
        )
        messages_count = result.scalar() or 0
        
        # Count orders
        result = await self.db.execute(
            select(func.count(Order.id))
            .join(Project, Order.project_id == Project.id)
            .where(
                and_(
                    Project.owner_id == user_id,
                    Order.created_at >= month_start
                )
            )
        )
        orders_count = result.scalar() or 0
        
        # Count projects
        result = await self.db.execute(
            select(func.count(Project.id))
            .where(Project.owner_id == user_id)
        )
        projects_count = result.scalar() or 0
        
        # Get usage tracking record
        result = await self.db.execute(
            select(UsageTracking)
            .where(
                and_(
                    UsageTracking.user_id == user_id,
                    UsageTracking.period_start >= month_start
                )
            )
            .order_by(UsageTracking.created_at.desc())
            .limit(1)
        )
        usage_record = result.scalar_one_or_none()
        
        return {
            "messages": messages_count,
            "orders": orders_count,
            "projects": projects_count,
            "ai_requests": usage_record.ai_requests if usage_record else 0,
            "ai_tokens": usage_record.ai_tokens_used if usage_record else 0,
            "storage_gb": usage_record.storage_used_gb if usage_record else 0.0
        }
    
    async def check_all_limits(self, user_id: UUID) -> Dict[str, Dict[str, Any]]:
        """Check all resource limits for user."""
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Get usage
        usage = await self.get_current_usage(user_id)
        
        # Check each limit
        tier = await self._get_user_tier(user)
        return {
            "messages": check_limit(tier, "messages", usage["messages"]),
            "orders": check_limit(tier, "orders", usage["orders"]),
            "projects": check_limit(tier, "projects", usage["projects"]),
            "ai_requests": check_limit(tier, "ai_requests", usage["ai_requests"]),
            "storage_gb": check_limit(tier, "storage_gb", int(usage["storage_gb"]))
        }
    
    async def can_use_resource(self, user_id: UUID, resource: str) -> bool:
        """Check if user can use a specific resource."""
        limits_status = await self.check_all_limits(user_id)
        
        if resource in limits_status:
            return limits_status[resource]["allowed"]
        
        return True
    
    async def can_use_feature(self, user_id: UUID, feature: str) -> bool:
        """Check if user has access to a feature."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        tier = await self._get_user_tier(user)
        return check_feature_access(tier, feature)
    
    async def track_usage(
        self,
        user_id: UUID,
        resource_type: str,
        amount: int = 1
    ) -> None:
        """Track usage for billing."""
        # Get or create current month usage record
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        # Get subscription
        result = await self.db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            return
        
        # Get or create usage record
        result = await self.db.execute(
            select(UsageTracking)
            .where(
                and_(
                    UsageTracking.user_id == user_id,
                    UsageTracking.period_start == month_start
                )
            )
        )
        usage = result.scalar_one_or_none()
        
        if not usage:
            usage = UsageTracking(
                subscription_id=subscription.id,
                user_id=user_id,
                period_start=month_start,
                period_end=month_end
            )
            self.db.add(usage)
        
        # Update usage
        if resource_type == "messages_sent":
            usage.messages_sent += amount
        elif resource_type == "messages_received":
            usage.messages_received += amount
        elif resource_type == "orders":
            usage.orders_created += amount
        elif resource_type == "ai_requests":
            usage.ai_requests += amount
        elif resource_type == "ai_tokens":
            usage.ai_tokens_used += amount
        
        await self.db.commit()
    
    async def upgrade_tier(
        self,
        user_id: UUID,
        new_tier: SubscriptionTier
    ) -> Dict[str, Any]:
        """Upgrade/downgrade user tier."""
        return await self.create_subscription(user_id, new_tier)
    
    async def cancel_subscription(self, user_id: UUID) -> Dict[str, Any]:
        """Cancel user subscription (downgrade to free at end of period)."""
        result = await self.db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise ValueError("No active subscription")
        
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.utcnow()
        
        # Update user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        user.subscription_status = SubscriptionStatus.CANCELLED
        
        await self.db.commit()
        
        logger.info("Subscription cancelled", user_id=str(user_id))
        
        return {
            "cancelled": True,
            "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None,
            "message": "Subscription will remain active until expiration date"
        }
    
    async def track_ai_usage(
        self,
        user_id: UUID,
        tokens_input: int,
        tokens_output: int,
        model_used: str = "gemini-2.0-flash"
    ) -> None:
        """Track AI usage with token counts."""
        total_tokens = tokens_input + tokens_output
        
        # Track AI request
        await self.track_usage(user_id, "ai_requests", 1)
        
        # Track tokens
        await self.track_usage(user_id, "ai_tokens", total_tokens)
        
        logger.debug(
            "AI usage tracked",
            user_id=str(user_id),
            tokens=total_tokens,
            model=model_used
        )
    
    async def check_and_enforce_limit(
        self,
        user_id: UUID,
        resource: str
    ) -> Dict[str, Any]:
        """
        Check if user can use resource and enforce limit.
        Returns: {allowed: bool, reason: str, usage: dict}
        """
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {"allowed": False, "reason": "User not found"}
        
        # Check limit
        limits_status = await self.check_all_limits(user_id)
        
        if resource not in limits_status:
            return {"allowed": True, "reason": "No limit for this resource"}
        
        status = limits_status[resource]
        
        if not status["allowed"]:
            tier = await self._get_user_tier(user)
            tier_info = get_tier_info(tier)
            return {
                "allowed": False,
                "reason": f"Limit exceeded. Upgrade to {tier_info['name']} or higher.",
                "usage": status,
                "current_tier": tier.value,
                "upgrade_required": True
            }
        
        return {
            "allowed": True,
            "usage": status
        }
    
    async def calculate_monthly_overages(self, user_id: UUID) -> Dict[str, Any]:
        """Calculate overage charges for the current month."""
        from app.core.subscription_plans import calculate_overage_cost
        
        # Get user and usage
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        tier = await self._get_user_tier(user)
        usage = await self.get_current_usage(user_id)
        limits = TIER_LIMITS[tier]
        
        overages = {}
        total_overage_cost = 0.0
        
        # Calculate overages for each resource
        for resource in ["messages", "orders", "ai_requests", "storage_gb"]:
            used = usage.get(resource, 0)
            limit = limits.get(resource, 0)
            
            if limit == 999999:  # Unlimited
                continue
            
            if used > limit:
                overage_amount = used - limit
                cost = calculate_overage_cost(resource, overage_amount)
                overages[resource] = {
                    "limit": limit,
                    "used": used,
                    "overage": overage_amount,
                    "cost": cost
                }
                total_overage_cost += cost
        
        # Update usage tracking record
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        result = await self.db.execute(
            select(UsageTracking)
            .where(
                and_(
                    UsageTracking.user_id == user_id,
                    UsageTracking.period_start == month_start
                )
            )
        )
        usage_record = result.scalar_one_or_none()
        
        if usage_record:
            usage_record.overage_charges = total_overage_cost
            usage_record.limits_exceeded = list(overages.keys())
            await self.db.commit()
        
        logger.info(
            "Monthly overages calculated",
            user_id=str(user_id),
            total_cost=total_overage_cost,
            overages=overages
        )
        
        return {
            "user_id": str(user_id),
            "period": month_start.isoformat(),
            "overages": overages,
            "total_cost": total_overage_cost
        }
    
    async def get_usage_percentage(self, user_id: UUID) -> Dict[str, float]:
        """Get usage as percentage of limits."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {}
        
        tier = await self._get_user_tier(user)
        usage = await self.get_current_usage(user_id)
        limits = TIER_LIMITS[tier]
        
        percentages = {}
        for resource in ["messages", "orders", "ai_requests", "projects"]:
            used = usage.get(resource, 0)
            limit = limits.get(resource, 0)
            
            if limit == 0 or limit == 999999:
                percentages[resource] = 0.0
            else:
                percentages[resource] = (used / limit) * 100
        
        return percentages
    
    async def should_send_usage_alert(self, user_id: UUID) -> Dict[str, Any]:
        """Check if user should receive usage alerts."""
        percentages = await self.get_usage_percentage(user_id)
        
        alerts = {}
        for resource, pct in percentages.items():
            if pct >= 100:
                alerts[resource] = {"level": "critical", "percentage": pct}
            elif pct >= 90:
                alerts[resource] = {"level": "warning", "percentage": pct}
            elif pct >= 80:
                alerts[resource] = {"level": "info", "percentage": pct}
        
        return {
            "should_alert": len(alerts) > 0,
            "alerts": alerts
        }
