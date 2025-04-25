from celery import Celery
from src.side_quest_py.api.config import settings

# Create Celery instance
celery_app = Celery(
    "side_quest",
    broker=settings.CELERY_BROKER_URL,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
