"""
Customer service logic for identity management.
"""
from typing import Dict, Any, List
from uuid import UUID
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CustomerProfile, Integration, IntegrationStatus
from app.services.integrations.facebook import FacebookClient

logger = structlog.get_logger(__name__)

async def refresh_customer_identities(db: AsyncSession, project_id: UUID) -> Dict[str, Any]:
    """
    Refresh identities for customers with generic names in a specific project.
    """
    logger.info("Starting customer identity refresh", project_id=str(project_id))
    
    # 1. Find customers with generic names for this project
    generic_names = ["Unknown", "Instagram User", "Facebook User", "Facebook Profile"]
    query = select(CustomerProfile).where(
        CustomerProfile.project_id == project_id,
        (CustomerProfile.name.in_(generic_names)) | (CustomerProfile.name == None)
    )
    result = await db.execute(query)
    customers = result.scalars().all()
    
    logger.info(f"Found {len(customers)} customers with generic names", project_id=str(project_id))
    
    if not customers:
        return {
            "status": "success",
            "updated_count": 0,
            "message": "All customers already have unique names."
        }

    # 2. Iterate and fetch
    updated_count = 0
    errors = []
    
    # Cache clients for providers to avoid re-initializing
    clients = {}

    for customer in customers:
        platform = None
        if customer.platform_accounts:
            if "instagram" in customer.platform_accounts:
                platform = "instagram"
            elif "facebook" in customer.platform_accounts:
                platform = "facebook"
        
        if not platform:
            continue
            
        sender_id = customer.platform_accounts.get(platform)
        if not sender_id:
            continue
            
        try:
            # Get or initialize client for this platform
            if platform not in clients:
                int_query = select(Integration).where(
                    Integration.project_id == project_id,
                    Integration.provider == platform,
                    Integration.status == IntegrationStatus.CONNECTED
                )
                int_result = await db.execute(int_query)
                integration = int_result.scalars().first()
                
                if integration:
                    clients[platform] = FacebookClient(integration.config)
                else:
                    logger.warning(f"No connected {platform} integration found", project_id=str(project_id))
                    continue
            
            client = clients[platform]
            profile = await client.get_user_profile(sender_id, platform=platform)
            
            real_name = None
            if platform == "instagram":
                real_name = profile.get("username") or profile.get("name")
            else:
                real_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
            
            if real_name and real_name not in generic_names:
                logger.info(f"Resolved identity: {customer.name} -> {real_name}", customer_id=str(customer.id))
                customer.name = real_name
                db.add(customer)
                updated_count += 1
            else:
                logger.info("Could not resolve real name", customer_id=str(customer.id))
                
        except Exception as e:
            logger.error(f"Error resolving {customer.id}", error=str(e))
            errors.append(str(e))

    if updated_count > 0:
        await db.commit()
    
    return {
        "status": "success",
        "updated_count": updated_count,
        "errors": errors if errors else None,
        "message": f"Successfully updated {updated_count} customer identities."
    }
