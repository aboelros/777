"""
Subscription check dependencies for API endpoints.
Use these to enforce subscription limits on endpoints.
"""

from typing import Callable
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.subscription_service import SubscriptionService


async def check_message_limit(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> str:
    """
    Dependency to check message sending limit.
    Raises HTTPException if limit exceeded.
    """
    subscription_service = SubscriptionService(db)
    
    result = await subscription_service.check_and_enforce_limit(
        UUID(user_id), "messages"
    )
    
    if not result["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "limit_exceeded",
                "message": result["reason"],
                "upgrade_required": True,
                "current_tier": result.get("current_tier"),
                "usage": result.get("usage")
            }
        )
    
    return user_id


async def check_order_limit(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> str:
    """
    Dependency to check order creation limit.
    Raises HTTPException if limit exceeded.
    """
    subscription_service = SubscriptionService(db)
    
    result = await subscription_service.check_and_enforce_limit(
        UUID(user_id), "orders"
    )
    
    if not result["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "limit_exceeded",
                "message": result["reason"],
                "upgrade_required": True,
                "current_tier": result.get("current_tier"),
                "usage": result.get("usage")
            }
        )
    
    return user_id


async def check_ai_limit(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> str:
    """
    Dependency to check AI request limit.
    Raises HTTPException if limit exceeded.
    """
    subscription_service = SubscriptionService(db)
    
    result = await subscription_service.check_and_enforce_limit(
        UUID(user_id), "ai_requests"
    )
    
    if not result["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "limit_exceeded",
                "message": result["reason"],
                "upgrade_required": True,
                "current_tier": result.get("current_tier"),
                "usage": result.get("usage")
            }
        )
    
    return user_id


async def check_project_limit(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> str:
    """
    Dependency to check project creation limit.
    Raises HTTPException if limit exceeded.
    """
    subscription_service = SubscriptionService(db)
    
    result = await subscription_service.check_and_enforce_limit(
        UUID(user_id), "projects"
    )
    
    if not result["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "limit_exceeded",
                "message": result["reason"],
                "upgrade_required": True,
                "current_tier": result.get("current_tier"),
                "usage": result.get("usage")
            }
        )
    
    return user_id


async def check_feature_access(feature: str):
    """
    Create a dependency to check feature access.
    
    Usage:
        @router.post("/", dependencies=[Depends(check_feature_access("api_access"))])
    """
    async def _check(
        user_id: str = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
    ) -> str:
        subscription_service = SubscriptionService(db)
        
        has_access = await subscription_service.can_use_feature(UUID(user_id), feature)
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "feature_not_available",
                    "message": f"Your plan doesn't include {feature}. Please upgrade.",
                    "feature": feature,
                    "upgrade_required": True
                }
            )
        
        return user_id
    
    return _check


async def get_subscription_service(
    db: AsyncSession = Depends(get_db)
) -> SubscriptionService:
    """Get subscription service instance."""
    return SubscriptionService(db)
