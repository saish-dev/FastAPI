"""
Celery application configuration.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "fastapi_app",
    broker=str(settings.CELERY_BROKER_URL),
    backend=str(settings.CELERY_RESULT_BACKEND),
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])


# Example task
@celery_app.task(name="app.tasks.example_task")
def example_task(x: int, y: int) -> int:
    """
    Example Celery task.

    Args:
        x: First number
        y: Second number

    Returns:
        Sum of x and y
    """
    return x + y
