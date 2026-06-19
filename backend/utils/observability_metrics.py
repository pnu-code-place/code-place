import logging

from prometheus_client import Counter, Histogram, REGISTRY
from prometheus_client.core import GaugeMetricFamily
from django.conf import settings
from redis import Redis
from redis.sentinel import Sentinel

from utils.cache import cache
from utils.constants import CacheKey

logger = logging.getLogger(__name__)

CELERY_BROKER_QUEUE_KEY = "celery"

HTTP_REQUESTS_TOTAL = Counter(
    "codeplace_http_requests_total",
    "Total backend HTTP requests.",
    ["method", "endpoint", "status_code"],
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "codeplace_http_request_duration_seconds",
    "Backend HTTP request duration.",
    ["method", "endpoint"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)
AI_HINT_REQUESTS_TOTAL = Counter(
    "codeplace_ai_hint_requests_total",
    "Total backend AI hint streaming requests to the LLM service.",
    ["status"],
)
AI_HINT_DURATION_SECONDS = Histogram(
    "codeplace_ai_hint_duration_seconds",
    "Backend AI hint streaming duration.",
    ["status"],
    buckets=(0.5, 1, 2, 5, 10, 30, 60, 120, 300, 600),
)
AI_HINT_API_OUTCOME_TOTAL = Counter(
    "codeplace_ai_hint_api_outcome_total",
    "Total user-facing AI hint API outcomes.",
    ["status", "scope"],
)
SUBMISSION_CREATE_OUTCOME_TOTAL = Counter(
    "codeplace_submission_create_outcome_total",
    "Total user-facing submission create API outcomes.",
    ["status", "scope"],
)
JUDGE_TASK_OUTCOME_TOTAL = Counter(
    "codeplace_judge_task_outcome_total",
    "Total Celery judge task outcomes.",
    ["status", "scope"],
)


class CodePlaceCollector:

    def describe(self):
        yield GaugeMetricFamily(
            "codeplace_waiting_queue_length",
            "Number of submissions waiting because no judge-server was available.",
        )
        yield GaugeMetricFamily(
            "codeplace_celery_broker_queue_length",
            "Number of Celery tasks waiting in the Redis broker default queue.",
        )

    def collect(self):
        yield self._waiting_queue_length()
        yield self._celery_broker_queue_length()

    def _waiting_queue_length(self):
        metric = GaugeMetricFamily(
            "codeplace_waiting_queue_length",
            "Number of submissions waiting because no judge-server was available.",
        )
        try:
            metric.add_metric([], cache.llen(CacheKey.waiting_queue) or 0)
        except Exception as e:
            logger.warning("Failed to collect waiting queue length: %s", e)
            metric.add_metric([], 0)
        return metric

    def _celery_broker_queue_length(self):
        metric = GaugeMetricFamily(
            "codeplace_celery_broker_queue_length",
            "Number of Celery tasks waiting in the Redis broker default queue.",
        )
        try:
            metric.add_metric([], self._celery_broker_client().llen(CELERY_BROKER_QUEUE_KEY) or 0)
        except Exception as e:
            logger.warning("Failed to collect Celery broker queue length: %s", e)
            metric.add_metric([], 0)
        return metric

    @staticmethod
    def _celery_broker_client():
        if getattr(settings, "REDIS_USE_SENTINEL", False):
            sentinel = Sentinel(
                getattr(settings, "REDIS_SENTINEL_HOSTS"),
                socket_timeout=1,
            )
            return sentinel.master_for(
                getattr(settings, "REDIS_SENTINEL_MASTER_NAME", "mymaster"),
                db=4,
                socket_timeout=1,
            )
        return Redis.from_url(getattr(settings, "CELERY_BROKER_URL"))


def register_codeplace_metrics():
    if getattr(register_codeplace_metrics, "_registered", False):
        return
    try:
        REGISTRY.register(CodePlaceCollector())
    except ValueError:
        logger.debug("CodePlace metrics collector is already registered")
    register_codeplace_metrics._registered = True
