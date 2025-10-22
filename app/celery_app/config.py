from celery import Celery

celery_app = Celery(
    "celery",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery_app.conf.update(
    task_serializer="json",
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    result_expires=3600,
    timezone="UTC",
    broker_connection_retry_on_startup=True,
)

celery_app.autodiscover_tasks(["app.celery_media_tasks"])