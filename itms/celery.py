import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itms.settings')

app = Celery('itms')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat configuration
app.conf.beat_schedule = {
    'health-check-every-5-minutes': {
        'task': 'itms_app.tasks.health_check_task',
        'schedule': 300.0,  # 5 minutes
    },
    'cleanup-old-logs': {
        'task': 'itms_app.tasks.cleanup_old_logs',
        'schedule': 86400.0,  # daily
    },
}

app.conf.timezone = settings.TIME_ZONE

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')