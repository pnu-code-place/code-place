import os
import celery
from celery.signals import task_postrun, task_prerun

from utils.observability_context import reset_request_id, set_request_id
from utils.observability_tracing import configure_opentelemetry

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
configure_opentelemetry("codeplace-celery")

app = celery.Celery('scheduler')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

_request_id_tokens = {}


@task_prerun.connect
def bind_request_id(task_id=None, task=None, **kwargs):
    headers = getattr(getattr(task, "request", None), "headers", None) or {}
    request_id = headers.get("x-request-id")
    if task_id and request_id:
        _request_id_tokens[task_id] = set_request_id(request_id)


@task_postrun.connect
def unbind_request_id(task_id=None, **kwargs):
    token = _request_id_tokens.pop(task_id, None)
    if token is not None:
        reset_request_id(token)
