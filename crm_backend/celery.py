import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_backend.settings')

app = Celery('crm_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure periodic tasks for Render
app.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'leads.tasks.send_daily_reminders',
        'schedule': crontab(hour=9, minute=0),  # Run at 9 AM UTC daily
    },
    'cleanup-old-reminders': {
        'task': 'leads.tasks.cleanup_completed_reminders',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight UTC daily
    },
    'update-lead-statuses': {
        'task': 'leads.tasks.update_stale_lead_statuses',
        'schedule': crontab(hour=3, minute=0),  # Run at 3 AM UTC daily
    },
}

# Redis connection pool settings for Render
app.conf.broker_pool_limit = 1
app.conf.broker_heartbeat = None
app.conf.broker_connection_timeout = 30
app.conf.worker_prefetch_multiplier = 1

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')