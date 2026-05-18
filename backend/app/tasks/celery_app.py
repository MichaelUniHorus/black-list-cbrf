from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "openblack",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.enrichment_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)

celery_app.conf.beat_schedule = {
    "sync-cbr-daily": {
        "task": "app.tasks.enrichment_tasks.sync_cbr_data",
        "schedule": crontab(hour=2, minute=0),
        "options": {"expires": 3600},
    },
    "enrich-all-organizations-daily": {
        "task": "app.tasks.enrichment_tasks.enrich_all_organizations",
        "schedule": crontab(hour=3, minute=0),
        "options": {"expires": 7200},
    },
}
