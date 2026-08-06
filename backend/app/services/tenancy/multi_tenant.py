"""
Multi-Tenancy Service
Provides tenant isolation, resource quotas, and tenant-specific configurations.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
# TODO: Uncomment after creating Tenant, TenantQuota, TenantConfig models
# from app.db.models import Tenant, TenantQuota, TenantConfig
import structlog

logger = structlog.get_logger(__name__)


class TenantManager:
    """
    Manages multi-tenant operations including isolation and quotas.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_tenant(
        self,
        name: str,
        subdomain: str,
        plan: str = 'starter',
        owner_id: int = None
    ) -> Dict[str, Any]:
        """
        Create a new tenant.
        
        Args:
            name: Tenant name
            subdomain: Unique subdomain
            plan: Subscription plan (starter, professional, enterprise)
            owner_id: Owner user ID
            
        Returns:
            Created tenant data
        """
        # Check subdomain availability
        result = await self.db.execute(
            select(Tenant).where(Tenant.subdomain == subdomain)
        )
        if result.scalar_one_or_none():
            raise ValueError(f"Subdomain '{subdomain}' already taken")
        
        # Create tenant
        tenant = Tenant(
            name=name,
            subdomain=subdomain,
            plan=plan,
            owner_id=owner_id,
            status='active',
            created_at=datetime.utcnow()
        )
        
        self.db.add(tenant)
        await self.db.flush()
        
        # Set default quotas based on plan
        await self._set_default_quotas(tenant.id, plan)
        
        # Set default configuration
        await self._set_default_config(tenant.id)
        
        await self.db.commit()
        
        logger.info(
            "Tenant created",
            tenant_id=tenant.id,
            subdomain=subdomain,
            plan=plan
        )
        
        return {
            'id': tenant.id,
            'name': tenant.name,
            'subdomain': tenant.subdomain,
            'plan': tenant.plan,
            'status': tenant.status
        }
    
    async def _set_default_quotas(self, tenant_id: int, plan: str):
        """Set default resource quotas based on plan using existing subscription system."""
        from app.domains.billing.models import SubscriptionTier
        from app.core.subscription_plans import TIER_LIMITS
        
        # Map plan names to SubscriptionTier enum
        plan_mapping = {
            'free': SubscriptionTier.FREE,
            'starter': SubscriptionTier.STARTER,
            'growth': SubscriptionTier.GROWTH,
            'professional': SubscriptionTier.PROFESSIONAL,
            'scale': SubscriptionTier.SCALE,
            'business': SubscriptionTier.BUSINESS,
            'enterprise': SubscriptionTier.ENTERPRISE
        }
        
        tier = plan_mapping.get(plan.lower(), SubscriptionTier.FREE)
        limits = TIER_LIMITS[tier]
        
        # Create quota records for each resource
        quota_resources = {
            'max_users': limits['team_members'],
            'max_projects': limits['projects'],
            'max_messages_per_month': limits['messages'],
            'max_ai_requests_per_month': limits['ai_requests'],
            'max_storage_gb': limits['storage_gb'],
            'max_integrations': limits['integrations']
        }
        
        for resource, limit in quota_resources.items():
            quota = TenantQuota(
                tenant_id=tenant_id,
                resource=resource,
                limit=limit,
                current_usage=0
            )
            self.db.add(quota)
    
    async def _set_default_config(self, tenant_id: int):
        """Set default tenant configuration."""
        default_config = {
            'branding': {
                'logo_url': None,
                'primary_color': '#8B5CF6',
                'company_name': None
            },
            'features': {
                'ai_enabled': True,
                'analytics_enabled': True,
                'integrations_enabled': True,
                'custom_domain': False
            },
            'security': {
                'require_2fa': False,
                'sso_enabled': False,
                'session_timeout_minutes': 60,
                'ip_whitelist': []
            },
            'notifications': {
                'email_enabled': True,
                'slack_enabled': False,
                'webhook_url': None
            }
        }
        
        config = TenantConfig(
            tenant_id=tenant_id,
            config=default_config
        )
        self.db.add(config)
    
    async def check_quota(
        self,
        tenant_id: int,
        resource: str
    ) -> Dict[str, Any]:
        """
        Check if tenant has quota available for a resource.
        
        Args:
            tenant_id: Tenant ID
            resource: Resource name
            
        Returns:
            Quota status
        """
        result = await self.db.execute(
            select(TenantQuota).where(
                TenantQuota.tenant_id == tenant_id,
                TenantQuota.resource == resource
            )
        )
        quota = result.scalar_one_or_none()
        
        if not quota:
            return {'available': True, 'unlimited': True}
        
        # -1 means unlimited
        if quota.limit == -1:
            return {
                'available': True,
                'unlimited': True,
                'current': quota.current_usage
            }
        
        available = quota.current_usage < quota.limit
        
        return {
            'available': available,
            'unlimited': False,
            'current': quota.current_usage,
            'limit': quota.limit,
            'percentage': (quota.current_usage / quota.limit * 100) if quota.limit > 0 else 0
        }
    
    async def increment_usage(
        self,
        tenant_id: int,
        resource: str,
        amount: int = 1
    ):
        """Increment resource usage for a tenant."""
        result = await self.db.execute(
            select(TenantQuota).where(
                TenantQuota.tenant_id == tenant_id,
                TenantQuota.resource == resource
            )
        )
        quota = result.scalar_one_or_none()
        
        if quota and quota.limit != -1:
            quota.current_usage += amount
            await self.db.commit()
            
            # Check if approaching limit
            if quota.current_usage >= quota.limit * 0.8:
                logger.warning(
                    "Tenant approaching quota limit",
                    tenant_id=tenant_id,
                    resource=resource,
                    usage=quota.current_usage,
                    limit=quota.limit
                )
    
    async def get_tenant_config(self, tenant_id: int) -> Dict[str, Any]:
        """Get tenant configuration."""
        result = await self.db.execute(
            select(TenantConfig).where(TenantConfig.tenant_id == tenant_id)
        )
        config = result.scalar_one_or_none()
        
        return config.config if config else {}
    
    async def update_tenant_config(
        self,
        tenant_id: int,
        config_updates: Dict[str, Any]
    ):
        """Update tenant configuration."""
        result = await self.db.execute(
            select(TenantConfig).where(TenantConfig.tenant_id == tenant_id)
        )
        config = result.scalar_one_or_none()
        
        if config:
            # Merge updates
            current_config = config.config or {}
            for key, value in config_updates.items():
                if isinstance(value, dict) and key in current_config:
                    current_config[key].update(value)
                else:
                    current_config[key] = value
            
            config.config = current_config
            await self.db.commit()
            
            logger.info(
                "Tenant config updated",
                tenant_id=tenant_id,
                updates=list(config_updates.keys())
            )


class TenantIsolation:
    """
    Ensures data isolation between tenants.
    """
    
    @staticmethod
    def filter_by_tenant(query, tenant_id: int, model):
        """
        Add tenant filter to query for data isolation.
        
        Args:
            query: SQLAlchemy query
            tenant_id: Tenant ID to filter by
            model: Model class
            
        Returns:
            Filtered query
        """
        if hasattr(model, 'tenant_id'):
            return query.where(model.tenant_id == tenant_id)
        return query
    
    @staticmethod
    async def verify_tenant_access(
        db: AsyncSession,
        tenant_id: int,
        user_id: int
    ) -> bool:
        """
        Verify user has access to tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            user_id: User ID
            
        Returns:
            True if user has access
        """
        from app.domains.auth.models import User
        from app.domains.common.models import TenantMember
        
        # Check if user is tenant owner
        result = await db.execute(
            select(Tenant).where(
                Tenant.id == tenant_id,
                Tenant.owner_id == user_id
            )
        )
        if result.scalar_one_or_none():
            return True
        
        # Check if user is tenant member
        result = await db.execute(
            select(TenantMember).where(
                TenantMember.tenant_id == tenant_id,
                TenantMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none() is not None


class BillingIntegration:
    """
    Handles billing and subscription management.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_usage_cost(
        self,
        tenant_id: int,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """
        Calculate monthly usage cost for a tenant using existing subscription system.
        
        Args:
            tenant_id: Tenant ID
            month: Month number
            year: Year
            
        Returns:
            Cost breakdown
        """
        from app.domains.billing.models import SubscriptionTier
        from app.core.subscription_plans import TIER_PRICING, calculate_overage_cost
        
        # Get tenant plan
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            raise ValueError("Tenant not found")
        
        # Map plan to tier
        plan_mapping = {
            'free': SubscriptionTier.FREE,
            'starter': SubscriptionTier.STARTER,
            'growth': SubscriptionTier.GROWTH,
            'professional': SubscriptionTier.PROFESSIONAL,
            'scale': SubscriptionTier.SCALE,
            'business': SubscriptionTier.BUSINESS,
            'enterprise': SubscriptionTier.ENTERPRISE
        }
        
        tier = plan_mapping.get(tenant.plan.lower(), SubscriptionTier.FREE)
        pricing = TIER_PRICING[tier]
        base_cost = pricing['monthly_price']
        
        # Get usage
        result = await self.db.execute(
            select(TenantQuota).where(TenantQuota.tenant_id == tenant_id)
        )
        quotas = result.scalars().all()
        
        # Calculate overage costs using existing system
        overage_cost = 0
        overage_details = []
        
        resource_mapping = {
            'max_messages_per_month': 'messages',
            'max_ai_requests_per_month': 'ai_requests',
            'max_storage_gb': 'storage_gb',
            'max_projects': 'projects'
        }
        
        for quota in quotas:
            if quota.limit != -1 and quota.limit < 999999 and quota.current_usage > quota.limit:
                overage = quota.current_usage - quota.limit
                
                # Map to subscription system resource name
                resource_name = resource_mapping.get(quota.resource, quota.resource)
                cost = calculate_overage_cost(resource_name, overage)
                
                if cost > 0:
                    overage_cost += cost
                    overage_details.append({
                        'resource': quota.resource,
                        'overage': overage,
                        'cost': cost
                    })
        
        total_cost = base_cost + overage_cost
        
        return {
            'tenant_id': tenant_id,
            'plan': tenant.plan,
            'tier': tier.value,
            'base_cost': base_cost,
            'overage_cost': overage_cost,
            'total_cost': total_cost,
            'overage_details': overage_details,
            'period': f"{year}-{month:02d}"
        }
