"""
Usage Tracking Service
Tracks and calculates resource usage for subscription limits.
"""

from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import structlog

from app.db.models import (
    Project, Message, Order, Product, Integration,
    Subscription, SubscriptionTier, APILog
)
from app.core.subscription_plans import TIER_LIMITS, check_limit

logger = structlog.get_logger(__name__)


class UsageTracker:
    """Track and calculate resource usage for projects."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_project_usage(self, project_id: UUID) -> Dict[str, Any]:
        """
        Get current usage statistics for a project.
        
        Returns:
            dict with usage for: messages, orders, ai_requests, storage_gb, integrations
        """
        # Get message count (current month)
        from datetime import datetime, timedelta
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        result = await self.db.execute(
            select(func.count(Message.id))
            .where(Message.project_id == project_id)
            .where(Message.created_at >= month_start)
        )
        message_count = result.scalar() or 0
        
        # Get order count (current month)
        result = await self.db.execute(
            select(func.count(Order.id))
            .where(Order.project_id == project_id)
            .where(Order.created_at >= month_start)
        )
        order_count = result.scalar() or 0
        
        # Get AI request count (current month)
        result = await self.db.execute(
            select(func.sum(APILog.ai_tokens_used))
            .where(APILog.project_id == project_id)
            .where(APILog.created_at >= month_start)
        )
        ai_tokens = result.scalar() or 0
        # Convert tokens to requests (approximate: 1 request = ~1000 tokens)
        ai_requests = int(ai_tokens / 1000)
        
        # Get integration count
        result = await self.db.execute(
            select(func.count(Integration.id))
            .where(Integration.project_id == project_id)
        )
        integration_count = result.scalar() or 0
        
        # Calculate storage usage (approximate)
        # Messages: ~1KB each, Orders: ~2KB each, Products: ~5KB each
        result = await self.db.execute(
            select(func.count(Product.id))
            .where(Product.project_id == project_id)
        )
        product_count = result.scalar() or 0
        
        storage_bytes = (
            (message_count * 1024) +  # 1KB per message
            (order_count * 2048) +     # 2KB per order
            (product_count * 5120)     # 5KB per product
        )
        storage_gb = storage_bytes / (1024 ** 3)  # Convert to GB
        
        return {
            "messages": message_count,
            "orders": order_count,
            "ai_requests": ai_requests,
            "integrations": integration_count,
            "storage_gb": round(storage_gb, 3),
            "products": product_count
        }
    
    async def check_usage_limits(
        self,
        project_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Check current usage against subscription limits.
        
        Returns:
            dict with limit status for each resource
        """
        # Get user's subscription
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            # Default to FREE tier
            tier = SubscriptionTier.FREE
        else:
            tier = subscription.tier
        
        # Get current usage
        usage = await self.get_project_usage(project_id)
        
        # Check each limit
        limits = TIER_LIMITS.get(tier, TIER_LIMITS[SubscriptionTier.FREE])
        
        return {
            "tier": tier.value,
            "usage": usage,
            "limits": {
                "messages": check_limit(tier, "messages", usage["messages"]),
                "orders": check_limit(tier, "orders", usage["orders"]),
                "ai_requests": check_limit(tier, "ai_requests", usage["ai_requests"]),
                "integrations": check_limit(tier, "integrations", usage["integrations"]),
                "storage_gb": check_limit(tier, "storage_gb", int(usage["storage_gb"]))
            }
        }
    
    async def can_create_resource(
        self,
        project_id: UUID,
        user_id: UUID,
        resource_type: str
    ) -> bool:
        """
        Check if user can create a new resource (message, order, etc.).
        
        Args:
            project_id: Project ID
            user_id: User ID
            resource_type: Type of resource (messages, orders, ai_requests, etc.)
        
        Returns:
            bool: True if allowed, False if limit exceeded
        """
        limits_status = await self.check_usage_limits(project_id, user_id)
        resource_limit = limits_status["limits"].get(resource_type)
        
        if not resource_limit:
            return True  # No limit defined
        
        return resource_limit.get("allowed", True)
    
    async def get_user_total_usage(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get total usage across all user's projects.
        
        Returns:
            dict with total usage statistics
        """
        # Get all user's projects
        result = await self.db.execute(
            select(Project)
            .where(Project.owner_id == user_id)
        )
        projects = result.scalars().all()
        
        total_usage = {
            "messages": 0,
            "orders": 0,
            "ai_requests": 0,
            "integrations": 0,
            "storage_gb": 0.0,
            "projects": len(projects)
        }
        
        for project in projects:
            project_usage = await self.get_project_usage(project.id)
            total_usage["messages"] += project_usage["messages"]
            total_usage["orders"] += project_usage["orders"]
            total_usage["ai_requests"] += project_usage["ai_requests"]
            total_usage["integrations"] += project_usage["integrations"]
            total_usage["storage_gb"] += project_usage["storage_gb"]
        
        total_usage["storage_gb"] = round(total_usage["storage_gb"], 3)
        
        return total_usage


async def get_usage_tracker(db: AsyncSession) -> UsageTracker:
    """Factory function to get usage tracker instance."""
    return UsageTracker(db)
