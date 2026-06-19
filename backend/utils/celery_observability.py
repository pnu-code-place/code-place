import logging
import time

from celery import signals

from utils.cache import cache
from utils.observability_context import get_request_id, reset_request_id, set_request_id

logger = logging.getLogger("codeplace.celery_task")

CELERY_TASK_TOTAL_KEY = "observability:celery:task_total"
CELERY_TASK_RUNTIME_BUCKET_KEY = "observability:celery:task_runtime_bucket"
CELERY_TASK_RUNTIME_COUNT_KEY = "observability:celery:task_runtime_count"
CELERY_TASK_RUNTIME_SUM_KEY = "observability:celery:task_runtime_sum"
CELERY_TASK_RUNTIME_LAST_KEY = "observability:celery:task_runtime_last"
CELERY_TASK_LAST_SEEN_AT_KEY = "observability:celery:task_last_seen_at"
CELERY_TASK_RUNTIME_BUCKETS = (1, 3, 5, 10, 30, 60, 120, 300, 600, float("inf"))

_task_start_times = {}
_request_id_tokens = {}
_configured = False


def configure_celery_observability():
    global _configured
    if _configured:
        return
    signals.before_task_publish.connect(_on_before_task_publish, weak=False)
    signals.task_prerun.connect(_on_task_prerun, weak=False)
    signals.task_postrun.connect(_on_task_postrun, weak=False)
    signals.task_retry.connect(_on_task_retry, weak=False)
    _configured = True


def _task_name(task):
    return getattr(task, "name", None) or getattr(task, "__name__", None) or "unknown"


def _field(*parts):
    return "|".join(str(part) for part in parts)


def _hincrbyfloat(key, field, amount):
    client = cache.client.get_client(write=True)
    return client.hincrbyfloat(key, field, amount)


def _hsetfloat(key, field, value):
    client = cache.client.get_client(write=True)
    return client.hset(key, field, value)


def _record_task(task_name, status, duration_seconds=None):
    status = (status or "unknown").lower()
    try:
        cache.hincrby(CELERY_TASK_TOTAL_KEY, _field(task_name, status), 1)
        _hsetfloat(CELERY_TASK_LAST_SEEN_AT_KEY, _field(task_name, status), time.time())
        if duration_seconds is not None:
            _hincrbyfloat(CELERY_TASK_RUNTIME_SUM_KEY, task_name, duration_seconds)
            cache.hincrby(CELERY_TASK_RUNTIME_COUNT_KEY, task_name, 1)
            _hsetfloat(CELERY_TASK_RUNTIME_LAST_KEY, _field(task_name, status), duration_seconds)
            for bucket in CELERY_TASK_RUNTIME_BUCKETS:
                if duration_seconds <= bucket:
                    bucket_label = "+Inf" if bucket == float("inf") else str(bucket)
                    cache.hincrby(CELERY_TASK_RUNTIME_BUCKET_KEY, _field(task_name, bucket_label), 1)
    except Exception:
        logger.exception("failed to record celery task metric", extra={
            "task_name": task_name,
            "task_status": status,
        })


def _on_before_task_publish(headers=None, **kwargs):
    request_id = get_request_id()
    if request_id and headers is not None:
        headers["x-request-id"] = request_id


def _request_headers(task):
    request = getattr(task, "request", None)
    headers = getattr(request, "headers", None) or {}
    return headers if isinstance(headers, dict) else {}


def _on_task_prerun(task_id=None, task=None, **kwargs):
    if task_id:
        _task_start_times[task_id] = time.monotonic()
    request_id = _request_headers(task).get("x-request-id")
    if request_id and task_id:
        _request_id_tokens[task_id] = set_request_id(request_id)


def _on_task_postrun(task_id=None, task=None, state=None, **kwargs):
    task_name = _task_name(task)
    started_at = _task_start_times.pop(task_id, None)
    duration_seconds = None
    if started_at is not None:
        duration_seconds = max(time.monotonic() - started_at, 0)
    _record_task(task_name, state, duration_seconds)
    logger.info("celery task completed", extra={
        "task_id": task_id,
        "task_name": task_name,
        "task_status": (state or "unknown").lower(),
        "duration_ms": round(duration_seconds * 1000, 2) if duration_seconds is not None else None,
    })
    token = _request_id_tokens.pop(task_id, None)
    if token is not None:
        reset_request_id(token)


def _on_task_retry(request=None, reason=None, **kwargs):
    task_name = getattr(request, "task", None) or "unknown"
    task_id = getattr(request, "id", None)
    _record_task(task_name, "retry")
    logger.warning("celery task retry", extra={
        "task_id": task_id,
        "task_name": task_name,
        "task_status": "retry",
        "retry_reason": str(reason) if reason else None,
    })
