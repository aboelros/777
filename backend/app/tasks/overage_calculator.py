"""
Overage calculation background task.
Run this monthly to calculate and bill overage charges.
"""

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_async_session
from app.db.models import User, SubscriptionStatus
from app.services.subscription_service import SubscriptionService

logger = structlog.get_logger(__name__)


async def calculate_all_overages(db: AsyncSession):
    """
    Calculate overage charges for all active users.
    Should be run at the end of each billing period (monthly).
    """
    logger.info("Starting monthly overage calculation")
    
    # Get all active users
    result = await db.execute(
        select(User).where(
            User.subscription_status == SubscriptionStatus.ACTIVE
        )
    )
    users = result.scalars().all()
    
    subscription_service = SubscriptionService(db)
    
    total_processed = 0
    total_overages = 0.0
    errors = []
    
    for user in users:
        try:
            overages = await subscription_service.calculate_monthly_overages(user.id)
            
            if overages["total_cost"] > 0:
                total_overages += overages["total_cost"]
                logger.info(
                    "Overages calculated",
                    user_id=str(user.id),
                    email=user.email,
                    amount=overages["total_cost"]
                )
            
            total_processed += 1
            
        except Exception as e:
            logger.error(
                "Failed to calculate overages",
                user_id=str(user.id),
                error=str(e)
            )
            errors.append({
                "user_id": str(user.id),
                "error": str(e)
            })
    
    logger.info(
        "Monthly overage calculation complete",
        total_users=len(users),
        processed=total_processed,
        total_overages=total_overages,
        errors_count=len(errors)
    )
    
    return {
        "total_users": len(users),
        "processed": total_processed,
        "total_overages": total_overages,
        "errors": errors
    }


async def run_overage_calculation():
    """Entry point for running overage calculation."""
    async for db in get_async_session():
        try:
            result = await calculate_all_overages(db)
            return result
        finally:
            await db.close()


if __name__ == "__main__":
    import asyncio
    
    # Run overage calculation
    result = asyncio.run(run_overage_calculation())
    print(f"Overage calculation complete: {result}")
