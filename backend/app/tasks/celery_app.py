from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "qasyp",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.embedding_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_routes={
        "app.tasks.embedding_tasks.*": {"queue": "embeddings"},
    },
)
