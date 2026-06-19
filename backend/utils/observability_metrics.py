import logging

from prometheus_client import Counter, Histogram, REGISTRY
from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily, HistogramMetricFamily

from utils.cache import cache
from utils.constants import CacheKey

logger = logging.getLogger(__name__)

JUDGE_DURATION_BUCKETS = (1, 3, 5, 10, 30, 60, 120, 300, 600, float("inf"))
CELERY_BROKER_QUEUE_KEY = "celery"
JUDGE_DURATION_BUCKET_KEY = "codeplace:judge_duration_seconds_bucket"
JUDGE_DURATION_COUNT_KEY = "codeplace:judge_duration_seconds_count"
JUDGE_DURATION_SUM_KEY = "codeplace:judge_duration_seconds_sum"

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
        yield HistogramMetricFamily(
            "codeplace_submission_judge_duration_seconds",
            "Judge duration for submissions completed in the last 10 minutes.",
        )
        yield GaugeMetricFamily(
            "codeplace_redis_connected_clients",
            "Current Redis connected clients from INFO clients.",
        )
        yield GaugeMetricFamily(
            "codeplace_redis_max_clients",
            "Configured Redis maxclients from INFO clients or CONFIG GET maxclients.",
        )
        yield CounterMetricFamily(
            "codeplace_redis_rejected_connections_total",
            "Total Redis rejected connections from INFO stats.",
        )
        yield GaugeMetricFamily(
            "codeplace_observability_collector_success",
            "Whether each CodePlace custom metrics collector completed successfully.",
            labels=["collector"],
        )

    def collect(self):
        self._collector_success = {}
        yield self._waiting_queue_length()
        yield self._celery_broker_queue_length()
        yield self._judge_duration_histogram()
        yield from self._redis_health_metrics()
        yield self._collector_success_metric()

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
            self._mark_collector_success("waiting_queue", False)
        else:
            self._mark_collector_success("waiting_queue", True)
        return metric

    def _celery_broker_queue_length(self):
        metric = GaugeMetricFamily(
            "codeplace_celery_broker_queue_length",
            "Number of Celery tasks waiting in the Redis broker default queue.",
        )
        try:
            metric.add_metric([], cache.llen(CELERY_BROKER_QUEUE_KEY) or 0)
        except Exception as e:
            logger.warning("Failed to collect Celery broker queue length: %s", e)
            metric.add_metric([], 0)
            self._mark_collector_success("celery_broker_queue", False)
        else:
            self._mark_collector_success("celery_broker_queue", True)
        return metric

    def _judge_duration_histogram(self):
        metric = HistogramMetricFamily(
            "codeplace_submission_judge_duration_seconds",
            "Judge duration recorded by celery workers.",
        )
        try:
            duration_buckets = self._redis_hash(JUDGE_DURATION_BUCKET_KEY)
            duration_sum = self._float_or_zero(cache.get(JUDGE_DURATION_SUM_KEY, 0))
        except Exception as e:
            logger.warning("Failed to collect judge duration metrics: %s", e)
            duration_buckets = {}
            duration_sum = 0
            self._mark_collector_success("judge_duration", False)
        else:
            self._mark_collector_success("judge_duration", True)

        cumulative_buckets = []
        for bucket in JUDGE_DURATION_BUCKETS:
            label = "+Inf" if bucket == float("inf") else str(bucket)
            cumulative_buckets.append((label, self._float_or_zero(duration_buckets.get(label, 0))))
        metric.add_metric([], cumulative_buckets, duration_sum)
        return metric

    def _redis_health_metrics(self):
        connected_clients_metric = GaugeMetricFamily(
            "codeplace_redis_connected_clients",
            "Current Redis connected clients from INFO clients.",
        )
        max_clients_metric = GaugeMetricFamily(
            "codeplace_redis_max_clients",
            "Configured Redis maxclients from INFO clients or CONFIG GET maxclients.",
        )
        rejected_connections_metric = CounterMetricFamily(
            "codeplace_redis_rejected_connections_total",
            "Total Redis rejected connections from INFO stats.",
        )
        try:
            client = cache.client.get_client(write=False)
            info = client.info()
            connected_clients = float(info.get("connected_clients") or 0)
            rejected_connections = float(info.get("rejected_connections") or 0)
            max_clients = self._float_or_zero(info.get("maxclients"))
            if max_clients == 0:
                try:
                    raw_max_clients = client.config_get("maxclients")
                    max_clients = self._float_or_zero(raw_max_clients.get("maxclients"))
                except Exception as e:
                    logger.warning("Failed to collect Redis maxclients metric: %s", e)
                    redis_success = False
                else:
                    redis_success = True
            else:
                redis_success = True
        except Exception as e:
            logger.warning("Failed to collect Redis health metrics: %s", e)
            connected_clients = max_clients = rejected_connections = 0
            self._mark_collector_success("redis", False)
        else:
            self._mark_collector_success("redis", redis_success)

        connected_clients_metric.add_metric([], connected_clients)
        max_clients_metric.add_metric([], max_clients)
        rejected_connections_metric.add_metric([], rejected_connections)
        yield connected_clients_metric
        yield max_clients_metric
        yield rejected_connections_metric

    def _collector_success_metric(self):
        metric = GaugeMetricFamily(
            "codeplace_observability_collector_success",
            "Whether each CodePlace custom metrics collector completed successfully.",
            labels=["collector"],
        )
        collectors = (
            "waiting_queue",
            "celery_broker_queue",
            "judge_duration",
            "redis",
        )
        for collector in collectors:
            metric.add_metric([collector], 1 if self._collector_success.get(collector, False) else 0)
        return metric

    def _mark_collector_success(self, collector, success):
        if not hasattr(self, "_collector_success"):
            self._collector_success = {}
        self._collector_success[collector] = bool(success)

    @staticmethod
    def _redis_hash(key):
        values = cache.hgetall(key) or {}
        return {
            CodePlaceCollector._decode(field): CodePlaceCollector._decode(value)
            for field, value in values.items()
        }

    @staticmethod
    def _decode(value):
        if isinstance(value, bytes):
            return value.decode()
        return str(value)

    @staticmethod
    def _float_or_zero(value):
        parsed = CodePlaceCollector._float_or_none(value)
        return parsed if parsed is not None else 0.0

    @staticmethod
    def _float_or_none(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


def register_codeplace_metrics():
    if getattr(register_codeplace_metrics, "_registered", False):
        return
    try:
        REGISTRY.register(CodePlaceCollector())
    except ValueError:
        logger.debug("CodePlace metrics collector is already registered")
    register_codeplace_metrics._registered = True


def record_judge_duration(duration_seconds):
    try:
        duration = max(float(duration_seconds), 0)
        for bucket in JUDGE_DURATION_BUCKETS:
            if duration <= bucket:
                label = "+Inf" if bucket == float("inf") else str(bucket)
                cache.hincrby(JUDGE_DURATION_BUCKET_KEY, label, 1)
        cache.redis_incr(JUDGE_DURATION_COUNT_KEY, 1)
        cache.incrbyfloat(JUDGE_DURATION_SUM_KEY, duration)
    except Exception:
        logger.exception("Failed to record judge duration metric")
