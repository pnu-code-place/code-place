import logging

from prometheus_client import Counter, Histogram, REGISTRY
from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily
from django.conf import settings
from redis import Redis
from redis.sentinel import Sentinel

from utils.cache import cache
from utils.constants import CacheKey

logger = logging.getLogger(__name__)

CELERY_BROKER_QUEUE_KEY = "celery"
JUDGE_TASK_OUTCOME_KEY = "observability:judge_task_outcomes"

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
        yield CounterMetricFamily(
            "codeplace_judge_task_outcome",
            "Total Celery judge task outcomes stored in Redis.",
            labels=["status", "scope"],
        )
        yield GaugeMetricFamily(
            "codeplace_collector_success",
            "Whether the most recent custom metric collection succeeded.",
            labels=["collector"],
        )
        yield GaugeMetricFamily(
            "codeplace_redis_sentinel_health",
            "Whether Redis Sentinel can resolve the master and satisfy quorum.",
            labels=["check"],
        )

    def collect(self):
        success = GaugeMetricFamily(
            "codeplace_collector_success",
            "Whether the most recent custom metric collection succeeded.",
            labels=["collector"],
        )
        collectors = (
            ("waiting_queue", self._waiting_queue_length),
            ("celery_broker_queue", self._celery_broker_queue_length),
            ("judge_task_outcomes", self._judge_task_outcomes),
            ("redis_sentinel_health", self._redis_sentinel_health),
        )
        for name, collector in collectors:
            try:
                metric = collector()
            except Exception as e:
                logger.warning("Failed to collect %s: %s", name, e)
                success.add_metric([name], 0)
            else:
                success.add_metric([name], 1)
                yield metric
        yield success

    def _waiting_queue_length(self):
        metric = GaugeMetricFamily(
            "codeplace_waiting_queue_length",
            "Number of submissions waiting because no judge-server was available.",
        )
        metric.add_metric([], cache.llen(CacheKey.waiting_queue) or 0)
        return metric

    def _celery_broker_queue_length(self):
        metric = GaugeMetricFamily(
            "codeplace_celery_broker_queue_length",
            "Number of Celery tasks waiting in the Redis broker default queue.",
        )
        metric.add_metric([], self._celery_broker_client().llen(CELERY_BROKER_QUEUE_KEY) or 0)
        return metric

    @staticmethod
    def _judge_task_outcomes():
        metric = CounterMetricFamily(
            "codeplace_judge_task_outcome",
            "Total Celery judge task outcomes stored in Redis.",
            labels=["status", "scope"],
        )
        for raw_field, raw_value in cache.hgetall(JUDGE_TASK_OUTCOME_KEY).items():
            field = raw_field.decode() if isinstance(raw_field, bytes) else str(raw_field)
            value = raw_value.decode() if isinstance(raw_value, bytes) else raw_value
            status, scope = field.split(":", 1)
            metric.add_metric([status, scope], float(value))
        return metric

    @classmethod
    def _redis_sentinel_health(cls):
        if not getattr(settings, "REDIS_USE_SENTINEL", False):
            raise RuntimeError("Redis Sentinel monitoring is disabled")
        sentinel = cls._sentinel_client()
        master_name = getattr(settings, "REDIS_SENTINEL_MASTER_NAME", "mymaster")
        sentinel.discover_master(master_name)
        quorum_available = False
        for client in sentinel.sentinels:
            try:
                client.execute_command("SENTINEL", "CKQUORUM", master_name)
            except Exception:
                continue
            quorum_available = True
            break
        if not quorum_available:
            raise RuntimeError(f"Redis Sentinel quorum is unavailable for {master_name}")
        metric = GaugeMetricFamily(
            "codeplace_redis_sentinel_health",
            "Whether Redis Sentinel can resolve the master and satisfy quorum.",
            labels=["check"],
        )
        metric.add_metric(["master"], 1)
        metric.add_metric(["quorum"], 1)
        return metric

    @staticmethod
    def _sentinel_client():
        return Sentinel(
            getattr(settings, "REDIS_SENTINEL_HOSTS"),
            socket_timeout=1,
        )

    @staticmethod
    def _celery_broker_client():
        if getattr(settings, "REDIS_USE_SENTINEL", False):
            sentinel = CodePlaceCollector._sentinel_client()
            return sentinel.master_for(
                getattr(settings, "REDIS_SENTINEL_MASTER_NAME", "mymaster"),
                db=4,
                socket_timeout=1,
            )
        return Redis.from_url(getattr(settings, "CELERY_BROKER_URL"))


def record_judge_task_outcome(status, scope):
    try:
        cache.hincrby(JUDGE_TASK_OUTCOME_KEY, f"{status}:{scope}", 1)
    except Exception as e:
        logger.warning("Failed to persist judge task outcome metric: %s", e)


def register_codeplace_metrics():
    if getattr(register_codeplace_metrics, "_registered", False):
        return
    try:
        REGISTRY.register(CodePlaceCollector())
    except ValueError:
        logger.debug("CodePlace metrics collector is already registered")
    register_codeplace_metrics._registered = True
