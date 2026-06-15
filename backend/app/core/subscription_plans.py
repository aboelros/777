"""
Subscription tier definitions with pricing and limits.
7 Plans from $0 to $799/month - OPTIMIZED FOR PROFITABILITY
"""

from typing import Dict, Any
from app.db.models import SubscriptionTier


# Tier Pricing (Monthly)
TIER_PRICING = {
    SubscriptionTier.FREE: {
        "name": "Free",
        "monthly_price": 0,
        "annual_price": 0,
        "description": "Perfect for trying out the platform",
        "features": [
            "1 Project",
            "50 Messages/month",
            "5 Orders/month",
            "500 AI Requests/month",
            "2 Integrations",
            "100MB Storage",
            "Basic Analytics",
            "Community Support"
        ]
    },
    SubscriptionTier.STARTER: {
        "name": "Starter",
        "monthly_price": 29,
        "annual_price": 290,  # Save ~17%
        "description": "Great for small businesses getting started",
        "features": [
            "3 Projects",
            "1,000 Messages/month",
            "100 Orders/month",
            "10,000 AI Requests/month",
            "5 Integrations",
            "1GB Storage",
            "Advanced Analytics",
            "AI Auto-Responses",
            "Order Management",
            "Email Support"
        ]
    },
    SubscriptionTier.GROWTH: {
        "name": "Growth",
        "monthly_price": 59,
        "annual_price": 590,  # Save ~17%
        "description": "For growing businesses with increasing needs",
        "features": [
            "5 Projects",
            "5,000 Messages/month",
            "500 Orders/month",
            "50,000 AI Requests/month",
            "10 Integrations",
            "2.5GB Storage",
            "2 Team Members",
            "Advanced Analytics",
            "AI Auto-Responses",
            "Order Automation",
            "Social Media Management",
            "Conversation Memory (Basic)",
            "Priority Email Support"
        ]
    },
    SubscriptionTier.PROFESSIONAL: {
        "name": "Professional",
        "monthly_price": 119,
        "annual_price": 1190,  # Save ~17%
        "description": "For growing businesses with multiple channels",
        "features": [
            "10 Projects",
            "10,000 Messages/month",
            "1,000 Orders/month",
            "100,000 AI Requests/month",
            "Unlimited Integrations",
            "5GB Storage",
            "Advanced AI Automation",
            "Social Media Management",
            "Conversation Memory",
            "Customer Profiling",
            "Business Context Learning",
            "Priority Email Support",
            "Weekly Reports"
        ]
    },
    SubscriptionTier.SCALE: {
        "name": "Scale",
        "monthly_price": 199,
        "annual_price": 1990,  # Save ~17%
        "description": "For businesses ready to scale operations",
        "features": [
            "15 Projects",
            "25,000 Messages/month",
            "2,500 Orders/month",
            "250,000 AI Requests/month",
            "Unlimited Integrations",
            "10GB Storage",
            "4 Team Members",
            "Full AI Automation Suite",
            "Advanced Social Media Management",
            "Full Conversation Memory",
            "Customer Profiling",
            "Business Context Learning",
            "Bulk Operations",
            "API Access",
            "White-Label Options",
            "Phone & Email Support",
            "Daily Reports"
        ]
    },
    SubscriptionTier.BUSINESS: {
        "name": "Business",
        "monthly_price": 349,
        "annual_price": 3490,  # Save ~17%
        "description": "For established brands with high volume",
        "features": [
            "30 Projects",
            "100,000 Messages/month",
            "10,000 Orders/month",
            "1,000,000 AI Requests/month",
            "Unlimited Integrations",
            "50GB Storage",
            "10 Team Members",
            "Full AI Automation Suite",
            "Advanced Order Management",
            "Bulk Operations",
            "Custom AI Training",
            "Full API Access",
            "White-Label Options",
            "24/7 Phone & Email Support",
            "Real-time Reports",
            "Custom Dashboards",
            "Dedicated Success Manager"
        ]
    },
    SubscriptionTier.ENTERPRISE: {
        "name": "Enterprise",
        "monthly_price": 799,
        "annual_price": 7990,  # Save ~17%
        "description": "For large organizations with custom needs",
        "features": [
            "Unlimited Projects",
            "Unlimited Messages",
            "Unlimited Orders",
            "Unlimited AI Requests",
            "Unlimited Everything",
            "100GB+ Storage",
            "Unlimited Team Members",
            "Custom AI Models",
            "Dedicated Account Manager",
            "Custom Integrations",
            "SLA Guarantee",
            "24/7 Priority Support",
            "Real-time Reports",
            "Custom Development",
            "On-premise Option",
            "Advanced Security",
            "Compliance Support"
        ]
    }
}


# Usage Limits per Tier
TIER_LIMITS = {
    SubscriptionTier.FREE: {
        "messages": 50,
        "orders": 5,
        "ai_requests": 500,
        "projects": 1,
        "integrations": 2,
        "storage_gb": 0.1,
        "team_members": 1,
        "ai_automation": False,
        "advanced_reports": False,
        "social_media_management": False,
        "conversation_memory": False,
        "order_automation": False,
        "api_access": False,
        "white_label": False,
        "custom_ai": False
    },
    SubscriptionTier.STARTER: {
        "messages": 1000,
        "orders": 100,
        "ai_requests": 10000,
        "projects": 3,
        "integrations": 5,
        "storage_gb": 1.0,
        "team_members": 1,
        "ai_automation": True,
        "advanced_reports": True,
        "social_media_management": False,
        "conversation_memory": False,
        "order_automation": True,
        "api_access": False,
        "white_label": False,
        "custom_ai": False
    },
    SubscriptionTier.GROWTH: {
        "messages": 5000,
        "orders": 500,
        "ai_requests": 50000,
        "projects": 5,
        "integrations": 10,
        "storage_gb": 2.5,
        "team_members": 2,
        "ai_automation": True,
        "advanced_reports": True,
        "social_media_management": True,
        "conversation_memory": True,
        "order_automation": True,
        "api_access": False,
        "white_label": False,
        "custom_ai": False
    },
    SubscriptionTier.PROFESSIONAL: {
        "messages": 10000,
        "orders": 1000,
        "ai_requests": 100000,
        "projects": 10,
        "integrations": 999999,  # Unlimited
        "storage_gb": 5.0,
        "team_members": 3,
        "ai_automation": True,
        "advanced_reports": True,
        "social_media_management": True,
        "conversation_memory": True,
        "order_automation": True,
        "api_access": True,
        "white_label": False,
        "custom_ai": False
    },
    SubscriptionTier.SCALE: {
        "messages": 25000,
        "orders": 2500,
        "ai_requests": 250000,
        "projects": 15,
        "integrations": 999999,  # Unlimited
        "storage_gb": 10.0,
        "team_members": 4,
        "ai_automation": True,
        "advanced_reports": True,
        "social_media_management": True,
        "conversation_memory": True,
        "order_automation": True,
        "api_access": True,
        "white_label": True,
        "custom_ai": True
    },
    SubscriptionTier.BUSINESS: {
        "messages": 100000,
        "orders": 10000,
        "ai_requests": 1000000,
        "projects": 30,
        "integrations": 999999,  # Unlimited
        "storage_gb": 50.0,
        "team_members": 10,
        "ai_automation": True,
        "advanced_reports": True,
        "social_media_management": True,
        "conversation_memory": True,
        "order_automation": True,
        "api_access": True,
        "white_label": True,
        "custom_ai": True
    },
    SubscriptionTier.ENTERPRISE: {
        "messages": 999999999,  # Unlimited
        "orders": 999999999,  # Unlimited
        "ai_requests": 999999999,  # Unlimited
        "projects": 999999999,  # Unlimited
        "integrations": 999999999,  # Unlimited
        "storage_gb": 100.0,
        "team_members": 999999,  # Unlimited
        "ai_automation": True,
        "advanced_reports": True,
        "social_media_management": True,
        "conversation_memory": True,
        "order_automation": True,
        "api_access": True,
        "white_label": True,
        "custom_ai": True
    }
}


def get_tier_info(tier: SubscriptionTier) -> Dict[str, Any]:
    """Get complete information for a tier."""
    pricing = TIER_PRICING.get(tier, TIER_PRICING[SubscriptionTier.FREE])
    limits = TIER_LIMITS.get(tier, TIER_LIMITS[SubscriptionTier.FREE])
    
    return {
        "tier": tier.value,
        "name": pricing["name"],
        "monthly_price": pricing["monthly_price"],
        "annual_price": pricing["annual_price"],
        "description": pricing["description"],
        "features": pricing["features"],
        "limits": limits
    }


def get_all_tiers() -> list:
    """Get all available subscription tiers."""
    return [
        get_tier_info(tier) 
        for tier in [
            SubscriptionTier.FREE,
            SubscriptionTier.STARTER,
            SubscriptionTier.GROWTH,
            SubscriptionTier.PROFESSIONAL,
            SubscriptionTier.SCALE,
            SubscriptionTier.BUSINESS,
            SubscriptionTier.ENTERPRISE
        ]
    ]


def check_limit(tier: SubscriptionTier, resource: str, current_usage: int) -> Dict[str, Any]:
    """
    Check if usage is within tier limits.
    
    Returns:
        dict with: allowed (bool), limit (int), current (int), remaining (int)
    """
    limits = TIER_LIMITS.get(tier, TIER_LIMITS[SubscriptionTier.FREE])
    limit = limits.get(resource, 0)
    
    # Unlimited check (very high number)
    if limit >= 999999:
        return {
            "allowed": True,
            "limit": limit,  # Return actual number (e.g. 999999999)
            "current": current_usage,
            "remaining": limit - current_usage
        }
    
    allowed = current_usage < limit
    remaining = max(0, limit - current_usage)
    
    return {
        "allowed": allowed,
        "limit": limit,
        "current": current_usage,
        "remaining": remaining,
        "percentage_used": round((current_usage / limit * 100) if limit > 0 else 0, 1)
    }


def check_feature_access(tier: SubscriptionTier, feature: str) -> bool:
    """Check if a feature is available for a tier."""
    limits = TIER_LIMITS.get(tier, TIER_LIMITS[SubscriptionTier.FREE])
    return limits.get(feature, False)


# Overage Pricing (when limits are exceeded)
OVERAGE_PRICING = {
    "messages": {
        "price_per_1000": 5.00,
        "description": "$5 per additional 1,000 messages"
    },
    "orders": {
        "price_per_100": 10.00,
        "description": "$10 per additional 100 orders"
    },
    "ai_requests": {
        "price_per_10000": 15.00,
        "description": "$15 per additional 10,000 AI requests"
    },
    "storage_gb": {
        "price_per_gb": 2.00,
        "description": "$2 per additional GB"
    },
    "projects": {
        "price_per_project": 25.00,
        "description": "$25 per additional project"
    },
    "team_members": {
        "price_per_member": 15.00,
        "description": "$15 per additional team member"
    }
}


def calculate_overage_cost(resource: str, overage_amount: int) -> float:
    """Calculate overage cost for exceeding limits."""
    if resource not in OVERAGE_PRICING:
        return 0.0
    
    pricing = OVERAGE_PRICING[resource]
    
    if resource == "messages":
        # Round up to nearest 1000
        units = (overage_amount + 999) // 1000
        return units * pricing["price_per_1000"]
    elif resource == "orders":
        # Round up to nearest 100
        units = (overage_amount + 99) // 100
        return units * pricing["price_per_100"]
    elif resource == "ai_requests":
        # Round up to nearest 10000
        units = (overage_amount + 9999) // 10000
        return units * pricing["price_per_10000"]
    elif resource == "storage_gb":
        return overage_amount * pricing["price_per_gb"]
    elif resource == "projects":
        return overage_amount * pricing["price_per_project"]
    elif resource == "team_members":
        return overage_amount * pricing["price_per_member"]
    
    return 0.0


def get_overage_info() -> Dict[str, Any]:
    """Get information about overage pricing."""
    return OVERAGE_PRICING
