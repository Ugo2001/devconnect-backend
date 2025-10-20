# ============================================================================
# devconnect/celery.py
# ============================================================================

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DevConnect.settings')

app = Celery('DevConnect')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'send-digest-emails': {
        'task': 'apps.notifications.tasks.send_daily_digest',
        'schedule': crontab(hour=9, minute=0),  # 9 AM daily
    },
    'cleanup-old-notifications': {
        'task': 'apps.notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=0, minute=0, day_of_week=0),  # Weekly on Sunday
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')