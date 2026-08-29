"""
Celery Task Application & Distributed Worker Configuration
"""

import logging
from celery import Celery
from backend.app.core.config import settings

logger = logging.getLogger("volt.celery")

celery_app = Celery(
    "volt_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "backend.app.workers.data_tasks",
        "backend.app.workers.training_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 Hour maximum per task
    worker_prefetch_multiplier=1,  # Fair task distribution for heavy ML jobs
    beat_schedule={
        "periodic-drift-audit": {
            "task": "backend.app.workers.data_tasks.audit_model_drift_task",
            "schedule": 3600 * settings.DRIFT_DETECTION_INTERVAL_HOURS,
        },
        "periodic-feature-materialization": {
            "task": "backend.app.workers.data_tasks.materialize_all_views_task",
            "schedule": 1800,  # Every 30 minutes
        },
    },
)
