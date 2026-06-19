import logging
from datetime import timedelta

from django.utils import timezone
from prometheus_client import Counter, Histogram, REGISTRY
from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily, HistogramMetricFamily

from utils.cache import cache
from utils.celery_observability import (
    CELERY_TASK_RUNTIME_BUCKET_KEY,
    CELERY_TASK_RUNTIME_BUCKETS,
    CELERY_TASK_RUNTIME_COUNT_KEY,
    CELERY_TASK_LAST_SEEN_AT_KEY,
    CELERY_TASK_RUNTIME_LAST_KEY,
    CELERY_TASK_RUNTIME_SUM_KEY,
    CELERY_TASK_TOTAL_KEY,
)
from utils.constants import CacheKey
from utils.judge_server_observability import load_judge_server_snapshots

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
FRONTEND_ERROR_TOTAL = Counter(
    "codeplace_frontend_error_total",
    "Total frontend runtime errors reported by browser clients.",
    ["surface", "error_type"],
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
        yield GaugeMetricFamily(
            "codeplace_judge_server_available",
            "Whether each judge-server is enabled and has a fresh heartbeat.",
            labels=["hostname"],
        )
        yield GaugeMetricFamily(
            "codeplace_judge_server_last_heartbeat_age_seconds",
            "Seconds since the latest judge-server heartbeat.",
            labels=["hostname"],
        )
        yield GaugeMetricFamily(
            "codeplace_judge_server_task_number",
            "Current task_number recorded for each judge-server.",
            labels=["hostname"],
        )
        yield HistogramMetricFamily(
            "codeplace_submission_judge_duration_seconds",
            "Judge duration for submissions completed in the last 10 minutes.",
        )
        yield CounterMetricFamily(
            "codeplace_celery_task_total",
            "Total Celery tasks grouped by task name and status.",
            labels=["task_name", "status"],
        )
        yield HistogramMetricFamily(
            "codeplace_celery_task_runtime_seconds",
            "Celery task runtime grouped by task name.",
            labels=["task_name"],
        )
        yield GaugeMetricFamily(
            "codeplace_celery_task_last_runtime_seconds",
            "Latest observed Celery task runtime grouped by task name and status.",
            labels=["task_name", "status"],
        )
        yield GaugeMetricFamily(
            "codeplace_redis_connected_clients",
            "Current Redis connected clients from INFO clients.",
        )
        yield GaugeMetricFamily(
            "codeplace_redis_max_clients",
            "Configured Redis maxclients from CONFIG GET maxclients.",
        )
        yield CounterMetricFamily(
            "codeplace_redis_rejected_connections_total",
            "Total Redis rejected connections from INFO stats.",
        )
        yield GaugeMetricFamily(
            "codeplace_celery_task_last_seen_age_seconds",
            "Seconds since each Celery task status was last observed.",
            labels=["task_name", "status"],
        )
        yield GaugeMetricFamily(
            "codeplace_celery_task_last_success_age_seconds",
            "Seconds since each Celery task last completed successfully.",
            labels=["task_name"],
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
        yield from self._judge_server_metrics()
        yield self._judge_duration_histogram()
        yield from self._celery_task_metrics()
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

    def _judge_server_metrics(self):
        available_metric = GaugeMetricFamily(
            "codeplace_judge_server_available",
            "Whether each judge-server is enabled and has a fresh heartbeat.",
            labels=["hostname"],
        )
        heartbeat_metric = GaugeMetricFamily(
            "codeplace_judge_server_last_heartbeat_age_seconds",
            "Seconds since the latest judge-server heartbeat.",
            labels=["hostname"],
        )
        task_metric = GaugeMetricFamily(
            "codeplace_judge_server_task_number",
            "Current task_number recorded for each judge-server.",
            labels=["hostname"],
        )
        snapshots = load_judge_server_snapshots()
        if snapshots is None:
            self._mark_collector_success("judge_server", False)
        else:
            self._mark_collector_success("judge_server", True)
        for snapshot in snapshots or []:
            hostname = snapshot["hostname"] or "unknown"
            available_metric.add_metric([hostname], snapshot["available"])
            heartbeat_metric.add_metric([hostname], snapshot["heartbeat_age"])
            task_metric.add_metric([hostname], snapshot["task_number"])
        yield available_metric
        yield heartbeat_metric
        yield task_metric

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

    def _celery_task_metrics(self):
        total_metric = CounterMetricFamily(
            "codeplace_celery_task_total",
            "Total Celery tasks grouped by task name and status.",
            labels=["task_name", "status"],
        )
        runtime_metric = HistogramMetricFamily(
            "codeplace_celery_task_runtime_seconds",
            "Celery task runtime grouped by task name.",
            labels=["task_name"],
        )
        last_runtime_metric = GaugeMetricFamily(
            "codeplace_celery_task_last_runtime_seconds",
            "Latest observed Celery task runtime grouped by task name and status.",
            labels=["task_name", "status"],
        )
        last_seen_age_metric = GaugeMetricFamily(
            "codeplace_celery_task_last_seen_age_seconds",
            "Seconds since each Celery task status was last observed.",
            labels=["task_name", "status"],
        )
        last_success_age_metric = GaugeMetricFamily(
            "codeplace_celery_task_last_success_age_seconds",
            "Seconds since each Celery task last completed successfully.",
            labels=["task_name"],
        )
        try:
            task_totals = self._redis_hash(CELERY_TASK_TOTAL_KEY)
            runtime_buckets = self._redis_hash(CELERY_TASK_RUNTIME_BUCKET_KEY)
            runtime_counts = self._redis_hash(CELERY_TASK_RUNTIME_COUNT_KEY)
            runtime_sums = self._redis_hash(CELERY_TASK_RUNTIME_SUM_KEY)
            last_runtimes = self._redis_hash(CELERY_TASK_RUNTIME_LAST_KEY)
            last_seen_at = self._redis_hash(CELERY_TASK_LAST_SEEN_AT_KEY)
        except Exception as e:
            logger.warning("Failed to collect Celery task metrics: %s", e)
            self._mark_collector_success("celery_task", False)
            yield total_metric
            yield runtime_metric
            yield last_runtime_metric
            yield last_seen_age_metric
            yield last_success_age_metric
            return
        else:
            self._mark_collector_success("celery_task", True)

        for field, value in task_totals.items():
            task_name, status = self._split_field(field, 2)
            total_metric.add_metric([task_name, status], self._float_or_zero(value))

        task_names = set(runtime_counts) | set(runtime_sums)
        for field in runtime_buckets:
            task_name, _ = self._split_field(field, 2)
            task_names.add(task_name)
        for task_name in sorted(task_names):
            cumulative_buckets = []
            for bucket in CELERY_TASK_RUNTIME_BUCKETS:
                bucket_label = "+Inf" if bucket == float("inf") else str(bucket)
                value = self._float_or_zero(runtime_buckets.get(self._join_field(task_name, bucket_label), 0))
                cumulative_buckets.append((bucket_label, value))
            runtime_metric.add_metric(
                [task_name],
                cumulative_buckets,
                self._float_or_zero(runtime_sums.get(task_name, 0)),
            )

        for field, value in last_runtimes.items():
            task_name, status = self._split_field(field, 2)
            last_runtime_metric.add_metric([task_name, status], self._float_or_zero(value))

        now_timestamp = timezone.now().timestamp()
        for field, value in last_seen_at.items():
            task_name, status = self._split_field(field, 2)
            seen_timestamp = self._float_or_none(value)
            if seen_timestamp is None:
                logger.warning("Skipping invalid Celery task last_seen_at metric: %s=%s", field, value)
                continue
            age_seconds = max(now_timestamp - seen_timestamp, 0)
            last_seen_age_metric.add_metric([task_name, status], age_seconds)
            if status == "success":
                last_success_age_metric.add_metric([task_name], age_seconds)

        yield total_metric
        yield runtime_metric
        yield last_runtime_metric
        yield last_seen_age_metric
        yield last_success_age_metric

    def _redis_health_metrics(self):
        connected_clients_metric = GaugeMetricFamily(
            "codeplace_redis_connected_clients",
            "Current Redis connected clients from INFO clients.",
        )
        max_clients_metric = GaugeMetricFamily(
            "codeplace_redis_max_clients",
            "Configured Redis maxclients from CONFIG GET maxclients.",
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
            max_clients = 0
            try:
                raw_max_clients = client.config_get("maxclients")
                max_clients = float(raw_max_clients.get("maxclients") or 0)
            except Exception as e:
                logger.warning("Failed to collect Redis maxclients metric: %s", e)
                self._mark_collector_success("redis", False)
        except Exception as e:
            logger.warning("Failed to collect Redis health metrics: %s", e)
            connected_clients = max_clients = rejected_connections = 0
            self._mark_collector_success("redis", False)
        else:
            if not getattr(self, "_collector_success", {}).get("redis", False):
                self._mark_collector_success("redis", True)

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
            "judge_server",
            "judge_duration",
            "celery_task",
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
    def _split_field(field, expected_parts):
        parts = field.split("|", expected_parts - 1)
        if len(parts) != expected_parts:
            return tuple(parts + ["unknown"] * (expected_parts - len(parts)))
        return tuple(parts)

    @staticmethod
    def _join_field(*parts):
        return "|".join(str(part) for part in parts)

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
