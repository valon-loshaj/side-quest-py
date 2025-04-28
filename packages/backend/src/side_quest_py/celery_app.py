"""
Celery app for Side Quest
"""

from celery import Celery
from celery.schedules import crontab
from src.side_quest_py.api.config import settings

# Create Celery instance
celery_app = Celery("side_quest", broker=settings.CELERY_BROKER_URL, include=["src.side_quest_py.tasks.email_tasks"])

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "send-daily-recap-emails": {
        "task": "src.side_quest_py.tasks.email_tasks.send_daily_recap_emails",
        # Run daily at 1:00 AM UTC
        "schedule": crontab(hour=1, minute=0),
    },
}
