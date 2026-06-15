"""
Subscription Management API endpoints.
Handles tier upgrades, usage tracking, and billing.
"""

from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id, require_role
from app.db.models import SubscriptionTier
from app.services.subscription_service import SubscriptionService
from app.core.subscription_plans import get_all_tiers, get_tier_info

router = APIRouter()
logger = structlog.get_logger(__name__)


class UpgradeRequest(BaseModel):
    """Tier upgrade request."""
    tier: str  # free, starter, professional, business, enterprise
    billing_cycle: str = "monthly"  # monthly, annually


class UsageTrackRequest(BaseModel):
    """Manual usage tracking."""
    resource_type: str  # messages_sent, orders, ai_requests
    amount: int = 1


# ============================================================================
# Subscription Plans
# ============================================================================

@router.get("/plans")
async def get_subscription_plans() -> Any:
    """
    Get all available subscription plans with pricing and features.
    
    **Returns:**
    - 5 tiers from Free to Enterprise
    - Pricing (monthly & annual)
    - Feature lists
    - Usage limits
    """
    try:
        plans = get_all_tiers()
        
        return {
            "success": True,
            "plans": plans,
            "total": len(plans)
        }
        
    except Exception as e:
        logger.error("Failed to get plans", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get plans: {str(e)}"
        )


@router.get("/plans/{tier}")
async def get_plan_details(tier: str) -> Any:
    """
    Get detailed information about a specific plan.
    
    **Tiers:**
    - free: $0/month
    - starter: $25/month
    - professional: $99/month
    - business: $249/month
    - enterprise: $500/month
    """
    try:
        # Parse tier
        try:
            tier_enum = SubscriptionTier[tier.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier: {tier}"
            )
        
        plan_info = get_tier_info(tier_enum)
        
        return {
            "success": True,
            **plan_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get plan details", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get plan: {str(e)}"
        )


# ============================================================================
# User Subscription Management
# ============================================================================

@router.get("/my-subscription")
async def get_my_subscription(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get current user's subscription details.
    
    **Returns:**
    - Current tier and limits
    - Usage statistics
    - Billing information
    - Next billing date
    """
    subscription_service = SubscriptionService(db)
    
    try:
        subscription = await subscription_service.get_user_subscription(UUID(user_id))
        
        if not subscription:
            # Return default free tier subscription
            from app.core.subscription_plans import get_tier_info
            from app.db.models import SubscriptionTier
            
            default_subscription = {
                "tier": SubscriptionTier.FREE.value,
                "status": "active",
                "limits": get_tier_info(SubscriptionTier.FREE)["limits"],
                "usage": {
                    "messages": 0,
                    "orders": 0,
                    "ai_requests": 0,
                    "projects": 0
                },
                "billing_cycle": "monthly",
                "next_billing_date": None
            }
            
            return {
                "success": True,
                "subscription": default_subscription
            }
        
        return {
            "success": True,
            "subscription": subscription
        }
        
    except Exception as e:
        logger.error("Failed to get subscription", error=str(e))
        # Return default free tier on error
        from app.core.subscription_plans import get_tier_info
        from app.db.models import SubscriptionTier
        
        default_subscription = {
            "tier": SubscriptionTier.FREE.value,
            "status": "active",
            "limits": get_tier_info(SubscriptionTier.FREE)["limits"],
            "usage": {
                "messages": 0,
                "orders": 0,
                "ai_requests": 0,
                "projects": 0
            },
            "billing_cycle": "monthly",
            "next_billing_date": None
        }
        
        return {
            "success": True,
            "subscription": default_subscription
        }


@router.post("/upgrade")
async def upgrade_subscription(
    request: UpgradeRequest,
    token_payload: dict = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Admin can upgrade self or we could look up user_id from token if we want strict self-upgrade for admins
    # But usually upgrade means "upgrade THIS user". 
    user_id = token_payload.get("sub")
    """
    Upgrade or change subscription tier.
    
    **Request:**
    ```json
    {
      "tier": "professional",
      "billing_cycle": "monthly"
    }
    ```
    
    **Billing Cycles:**
    - monthly: Billed every month
    - annually: Billed yearly (save ~17%)
    
    **Note:** In production, this would integrate with Stripe/payment gateway
    """
    subscription_service = SubscriptionService(db)
    
    try:
        # Parse tier
        try:
            tier_enum = SubscriptionTier[request.tier.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tier: {request.tier}"
            )
        
        # Validate billing cycle
        if request.billing_cycle not in ["monthly", "annually"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Billing cycle must be 'monthly' or 'annually'"
            )
        
        # Create/update subscription
        result = await subscription_service.create_subscription(
            user_id=UUID(user_id),
            tier=tier_enum,
            billing_cycle=request.billing_cycle
        )
        
        return {
            "success": True,
            **result,
            "message": f"Successfully upgraded to {request.tier.capitalize()}!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to upgrade subscription", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upgrade: {str(e)}"
        )


@router.post("/cancel")
async def cancel_subscription(
    token_payload: dict = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
) -> Any:
    user_id = token_payload.get("sub")
    """
    Cancel subscription (will downgrade to free at end of billing period).
    
    **Note:**
    - Access continues until current period ends
    - Automatically downgraded to Free tier
    - Data is preserved
    """
    subscription_service = SubscriptionService(db)
    
    try:
        result = await subscription_service.cancel_subscription(UUID(user_id))
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        logger.error("Failed to cancel subscription", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel: {str(e)}"
        )


# ============================================================================
# Usage & Limits
# ============================================================================

@router.get("/usage")
async def get_usage_stats(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get current month usage statistics.
    
    **Returns:**
    - Messages sent/received
    - Orders created
    - AI requests made
    - Storage used
    - Limits for each resource
    - Percentage used
    """
    subscription_service = SubscriptionService(db)
    
    try:
        usage = await subscription_service.get_current_usage(UUID(user_id))
        limits_status = await subscription_service.check_all_limits(UUID(user_id))
        
        return {
            "success": True,
            "usage": usage,
            "limits": limits_status
        }
        
    except Exception as e:
        logger.error("Failed to get usage", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage: {str(e)}"
        )


@router.post("/track-usage")
async def track_usage(
    request: UsageTrackRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Manually track usage (for testing/admin purposes).
    
    **Resource Types:**
    - messages_sent
    - messages_received
    - orders
    - ai_requests
    - ai_tokens
    """
    subscription_service = SubscriptionService(db)
    
    try:
        await subscription_service.track_usage(
            user_id=UUID(user_id),
            resource_type=request.resource_type,
            amount=request.amount
        )
        
        return {
            "success": True,
            "message": f"Tracked {request.amount} {request.resource_type}"
        }
        
    except Exception as e:
        logger.error("Failed to track usage", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track usage: {str(e)}"
        )


@router.get("/check-limit/{resource}")
async def check_resource_limit(
    resource: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Check if user can use a specific resource.
    
    **Resources:**
    - messages
    - orders
    - projects
    - ai_requests
    - storage_gb
    
    **Returns:**
    - allowed: Can use resource (bool)
    - limit: Maximum allowed
    - current: Current usage
    - remaining: How many left
    """
    subscription_service = SubscriptionService(db)
    
    try:
        can_use = await subscription_service.can_use_resource(UUID(user_id), resource)
        limits_status = await subscription_service.check_all_limits(UUID(user_id))
        
        resource_status = limits_status.get(resource, {
            "allowed": True,
            "limit": "unlimited",
            "current": 0,
            "remaining": "unlimited"
        })
        
        return {
            "success": True,
            "resource": resource,
            "can_use": can_use,
            **resource_status
        }
        
    except Exception as e:
        logger.error("Failed to check limit", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check limit: {str(e)}"
        )


@router.get("/check-feature/{feature}")
async def check_feature_access(
    feature: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Check if user has access to a feature.
    
    **Features:**
    - ai_automation
    - advanced_reports
    - social_media_management
    - conversation_memory
    - order_automation
    - api_access
    - white_label
    - custom_ai
    """
    subscription_service = SubscriptionService(db)
    
    try:
        has_access = await subscription_service.can_use_feature(UUID(user_id), feature)
        
        return {
            "success": True,
            "feature": feature,
            "has_access": has_access
        }
        
    except Exception as e:
        logger.error("Failed to check feature", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check feature: {str(e)}"
        )


# ============================================================================
# Overage & Billing
# ============================================================================

@router.get("/overages")
async def get_monthly_overages(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Calculate overage charges for current month.
    
    **Returns:**
    - Overage amount per resource
    - Total overage cost
    - Billing details
    """
    subscription_service = SubscriptionService(db)
    
    try:
        overages = await subscription_service.calculate_monthly_overages(UUID(user_id))
        
        return {
            "success": True,
            **overages
        }
        
    except Exception as e:
        logger.error("Failed to calculate overages", error=str(e))
        # Return default no overages on error
        return {
            "success": True,
            "has_overages": False,
            "overages": {},
            "total_cost": 0.0
        }


@router.get("/usage-percentage")
async def get_usage_percentage(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get usage as percentage of limits.
    
    **Returns:**
    - Percentage used for each resource
    - Helps visualize usage in UI
    """
    subscription_service = SubscriptionService(db)
    
    try:
        percentages = await subscription_service.get_usage_percentage(UUID(user_id))
        
        return {
            "success": True,
            "percentages": percentages
        }
        
    except Exception as e:
        logger.error("Failed to get usage percentage", error=str(e))
        # Return default percentages on error
        default_percentages = {
            "messages": 0.0,
            "orders": 0.0,
            "ai_requests": 0.0,
            "projects": 0.0,
            "integrations": 0.0,
            "storage_gb": 0.0
        }
        
        return {
            "success": True,
            "percentages": default_percentages
        }


@router.get("/usage-alerts")
async def check_usage_alerts(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Check if user should receive usage alerts.
    
    **Alert Levels:**
    - info: 80% used
    - warning: 90% used
    - critical: 100% used (limit exceeded)
    
    **Returns:**
    - Whether alerts should be sent
    - Alert details per resource
    """
    subscription_service = SubscriptionService(db)
    
    try:
        alerts = await subscription_service.should_send_usage_alert(UUID(user_id))
        
        return {
            "success": True,
            **alerts
        }
        
    except Exception as e:
        logger.error("Failed to check usage alerts", error=str(e))
        # Return default no alerts on error
        return {
            "success": True,
            "should_alert": False,
            "alerts": {},
            "highest_usage": 0.0
        }


@router.get("/check-limit/{resource}")
async def check_resource_limit(
    resource: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Check if user can use a resource (with enforcement).
    
    **Resources:**
    - messages
    - orders
    - ai_requests
    - projects
    
    **Returns:**
    - allowed: bool - Whether user can use resource
    - reason: str - Why if not allowed
    - usage: dict - Current usage stats
    - upgrade_required: bool - If upgrade needed
    """
    subscription_service = SubscriptionService(db)
    
    try:
        result = await subscription_service.check_and_enforce_limit(
            UUID(user_id), resource
        )
        
        return {
            "success": True,
            "resource": resource,
            **result
        }
        
    except Exception as e:
        logger.error("Failed to check limit", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check limit: {str(e)}"
        )
