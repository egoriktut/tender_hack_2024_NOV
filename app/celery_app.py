from celery import Celery
from app.config import settings  # Use absolute import

celery_app = Celery("app", broker=settings.BROKER_URL, backend=settings.BACKEND_URL)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["app.tasks"])  # Automatically discover tasks in app.tasks
