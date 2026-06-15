"""
Celery application configuration for background tasks.
"""

from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "ai_sales_commander",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    "sync-shopify-orders": {
        "task": "app.workers.tasks.sync_shopify_orders",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    "process-message-queue": {
        "task": "app.workers.tasks.process_message_queue",
        "schedule": crontab(minute="*"),  # Every minute
    },
    "generate-daily-reports": {
        "task": "app.workers.tasks.generate_daily_reports",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight
    },
    "cleanup-old-logs": {
        "task": "app.workers.tasks.cleanup_old_logs",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

if __name__ == "__main__":
    celery_app.start()
