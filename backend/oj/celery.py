import os
import celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')

app = celery.Celery('scheduler')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
