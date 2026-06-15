"""
Background task scheduler for order follow-ups.
Runs periodically to check and send follow-up messages.
"""

import asyncio
from datetime import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import AsyncSessionLocal
from app.services.smart_tracker import SmartTrackerService

logger = structlog.get_logger(__name__)


async def run_smart_tracker():
    """
    Background task that runs periodically to check for smart tracking rules.
    """
    logger.info("Smart Tracker scheduler started")
    
    while True:
        try:
            async with AsyncSessionLocal() as db:
                logger.info("Running Smart Tracker check...")
                tracker = SmartTrackerService(db)
                await tracker.run_checks()
                logger.info("Smart Tracker check complete")
        
        except Exception as e:
            logger.error("Error in Smart Tracker scheduler", error=str(e))
        
        # Wait 1 hour before next check
        await asyncio.sleep(3600)  # 3600 seconds = 1 hour


async def start_background_tasks():
    """
    Start all background tasks.
    Call this from main.py on startup.
    """
    asyncio.create_task(run_smart_tracker())
    logger.info("Background tasks started")
