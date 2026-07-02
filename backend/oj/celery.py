import os
import celery

from utils.observability_tracing import configure_opentelemetry

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
configure_opentelemetry("codeplace-celery")

app = celery.Celery('scheduler')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
