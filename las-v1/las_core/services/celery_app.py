"""
Celery Application Configuration for LAS Task Queue.
"""

from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Redis URL from environment or default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    'las_tasks',
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks
app.conf.beat_schedule = {
    'check-worker-health': {
        'task': 'services.celery_tasks.check_worker_health',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'cleanup-old-tasks': {
        'task': 'services.celery_tasks.cleanup_old_tasks',
        'schedule': crontab(hour='3', minute='0'),  # Daily at 3 AM
    },
}

if __name__ == '__main__':
    app.start()
