import logging
from datetime import timedelta

from django.db import connection
from django.db.models import Count, Min
from django.utils import timezone
from prometheus_client import Counter, Histogram, REGISTRY
from prometheus_client.core import GaugeMetricFamily, HistogramMetricFamily

from submission.models import JudgeStatus, Submission
from utils.cache import cache
from utils.celery_observability import (
    CELERY_TASK_RUNTIME_BUCKET_KEY,
    CELERY_TASK_RUNTIME_BUCKETS,
    CELERY_TASK_RUNTIME_COUNT_KEY,
    CELERY_TASK_RUNTIME_LAST_KEY,
    CELERY_TASK_RUNTIME_SUM_KEY,
    CELERY_TASK_TOTAL_KEY,
)
from utils.constants import CacheKey

logger = logging.getLogger(__name__)

JUDGE_DURATION_BUCKETS = (1, 3, 5, 10, 30, 60, 120, 300, 600, float("inf"))
JUDGE_STATUS_LABELS = {
    JudgeStatus.COMPILE_ERROR: "compile_error",
    JudgeStatus.WRONG_ANSWER: "wrong_answer",
    JudgeStatus.ACCEPTED: "accepted",
    JudgeStatus.CPU_TIME_LIMIT_EXCEEDED: "cpu_time_limit_exceeded",
    JudgeStatus.REAL_TIME_LIMIT_EXCEEDED: "real_time_limit_exceeded",
    JudgeStatus.MEMORY_LIMIT_EXCEEDED: "memory_limit_exceeded",
    JudgeStatus.RUNTIME_ERROR: "runtime_error",
    JudgeStatus.SYSTEM_ERROR: "system_error",
    JudgeStatus.PENDING: "pending",
    JudgeStatus.JUDGING: "judging",
    JudgeStatus.PARTIALLY_ACCEPTED: "partially_accepted",
}

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


class CodePlaceCollector:

    def describe(self):
        yield GaugeMetricFamily(
            "codeplace_submission_status_count",
            "Current number of submissions grouped by judge status.",
            labels=["status"],
        )
        yield GaugeMetricFamily(
            "codeplace_submission_oldest_age_seconds",
            "Age of the oldest submission in each in-flight judge status.",
            labels=["status"],
        )
        yield GaugeMetricFamily(
            "codeplace_waiting_queue_length",
            "Number of submissions waiting because no judge-server was available.",
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
        yield GaugeMetricFamily(
            "codeplace_celery_task_count",
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
            "codeplace_postgres_connections",
            "Current PostgreSQL connections for the active database.",
        )
        yield GaugeMetricFamily(
            "codeplace_postgres_max_connections",
            "Configured PostgreSQL max_connections.",
        )
        yield GaugeMetricFamily(
            "codeplace_postgres_long_transactions",
            "Current PostgreSQL transactions older than five minutes.",
        )
        yield GaugeMetricFamily(
            "codeplace_postgres_lock_waits",
            "Current PostgreSQL locks waiting to be granted.",
        )
        yield GaugeMetricFamily(
            "codeplace_redis_connected_clients",
            "Current Redis connected clients from INFO clients.",
        )
        yield GaugeMetricFamily(
            "codeplace_redis_max_clients",
            "Configured Redis maxclients from CONFIG GET maxclients.",
        )
        yield GaugeMetricFamily(
            "codeplace_redis_rejected_connections_total",
            "Total Redis rejected connections from INFO stats.",
        )

    def collect(self):
        yield from self._submission_status_count()
        yield self._submission_oldest_age_seconds()
        yield self._waiting_queue_length()
        yield from self._judge_server_metrics()
        yield self._judge_duration_histogram()
        yield from self._celery_task_metrics()
        yield from self._postgres_metrics()
        yield from self._redis_health_metrics()

    def _submission_status_count(self):
        metric = GaugeMetricFamily(
            "codeplace_submission_status_count",
            "Current number of submissions grouped by judge status.",
            labels=["status"],
        )
        try:
            counts = dict(Submission.objects.values_list("result").order_by("result").annotate(count=Count("id")))
        except Exception as e:
            logger.warning("Failed to collect submission status counts: %s", e)
            counts = {}
        for status_value, status_label in JUDGE_STATUS_LABELS.items():
            metric.add_metric([status_label], counts.get(status_value, 0))
        yield metric

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

    def _submission_oldest_age_seconds(self):
        metric = GaugeMetricFamily(
            "codeplace_submission_oldest_age_seconds",
            "Age of the oldest submission in each in-flight judge status.",
            labels=["status"],
        )
        now = timezone.now()
        status_map = {
            JudgeStatus.PENDING: "pending",
            JudgeStatus.JUDGING: "judging",
        }
        try:
            oldest_by_status = {
                row["result"]: row["oldest_create_time"]
                for row in Submission.objects.filter(
                    result__in=status_map.keys(),
                ).values("result").annotate(oldest_create_time=Min("create_time"))
            }
        except Exception as e:
            logger.warning("Failed to collect oldest submission age metrics: %s", e)
            oldest_by_status = {}

        for status_value, status_label in status_map.items():
            created_at = oldest_by_status.get(status_value)
            age_seconds = max((now - created_at).total_seconds(), 0) if created_at else 0
            metric.add_metric([status_label], age_seconds)
        return metric

    def _judge_server_metrics(self):
        from conf.models import JudgeServer

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
        now = timezone.now()
        try:
            servers = list(JudgeServer.objects.all())
        except Exception as e:
            logger.warning("Failed to collect judge-server metrics: %s", e)
            servers = []
        for server in servers:
            if server.is_disabled:
                continue
            hostname = server.hostname or "unknown"
            heartbeat_age = max((now - server.last_heartbeat).total_seconds(), 0)
            available = 1 if server.status == "normal" else 0
            available_metric.add_metric([hostname], available)
            heartbeat_metric.add_metric([hostname], heartbeat_age)
            task_metric.add_metric([hostname], server.task_number)
        yield available_metric
        yield heartbeat_metric
        yield task_metric

    def _judge_duration_histogram(self):
        metric = HistogramMetricFamily(
            "codeplace_submission_judge_duration_seconds",
            "Judge duration for submissions completed in the last 10 minutes.",
        )
        cutoff = timezone.now() - timedelta(minutes=10)
        durations = []
        try:
            submissions = Submission.objects.filter(
                judge_start_time__gte=cutoff,
                judge_start_time__isnull=False,
                judge_end_time__isnull=False,
            ).only("judge_start_time", "judge_end_time")
            for submission in submissions:
                durations.append(max((submission.judge_end_time - submission.judge_start_time).total_seconds(), 0))
        except Exception as e:
            logger.warning("Failed to collect judge duration metrics: %s", e)

        cumulative_buckets = []
        for bucket in JUDGE_DURATION_BUCKETS:
            label = "+Inf" if bucket == float("inf") else str(bucket)
            cumulative_buckets.append((label, sum(1 for duration in durations if duration <= bucket)))
        metric.add_metric([], cumulative_buckets, sum(durations))
        return metric

    def _celery_task_metrics(self):
        total_metric = GaugeMetricFamily(
            "codeplace_celery_task_count",
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
        try:
            task_totals = self._redis_hash(CELERY_TASK_TOTAL_KEY)
            runtime_buckets = self._redis_hash(CELERY_TASK_RUNTIME_BUCKET_KEY)
            runtime_counts = self._redis_hash(CELERY_TASK_RUNTIME_COUNT_KEY)
            runtime_sums = self._redis_hash(CELERY_TASK_RUNTIME_SUM_KEY)
            last_runtimes = self._redis_hash(CELERY_TASK_RUNTIME_LAST_KEY)
        except Exception as e:
            logger.warning("Failed to collect Celery task metrics: %s", e)
            yield total_metric
            yield runtime_metric
            yield last_runtime_metric
            return

        for field, value in task_totals.items():
            task_name, status = self._split_field(field, 2)
            total_metric.add_metric([task_name, status], float(value))

        task_names = set(runtime_counts) | set(runtime_sums)
        for field in runtime_buckets:
            task_name, _ = self._split_field(field, 2)
            task_names.add(task_name)
        for task_name in sorted(task_names):
            cumulative_buckets = []
            for bucket in CELERY_TASK_RUNTIME_BUCKETS:
                bucket_label = "+Inf" if bucket == float("inf") else str(bucket)
                value = float(runtime_buckets.get(self._join_field(task_name, bucket_label), 0))
                cumulative_buckets.append((bucket_label, value))
            runtime_metric.add_metric(
                [task_name],
                cumulative_buckets,
                float(runtime_sums.get(task_name, 0)),
            )

        for field, value in last_runtimes.items():
            task_name, status = self._split_field(field, 2)
            last_runtime_metric.add_metric([task_name, status], float(value))

        yield total_metric
        yield runtime_metric
        yield last_runtime_metric

    def _postgres_metrics(self):
        connections_metric = GaugeMetricFamily(
            "codeplace_postgres_connections",
            "Current PostgreSQL connections for the active database.",
        )
        max_connections_metric = GaugeMetricFamily(
            "codeplace_postgres_max_connections",
            "Configured PostgreSQL max_connections.",
        )
        long_transactions_metric = GaugeMetricFamily(
            "codeplace_postgres_long_transactions",
            "Current PostgreSQL transactions older than five minutes.",
        )
        lock_waits_metric = GaugeMetricFamily(
            "codeplace_postgres_lock_waits",
            "Current PostgreSQL locks waiting to be granted.",
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
                connections = cursor.fetchone()[0]
                cursor.execute("SELECT setting::float FROM pg_settings WHERE name = 'max_connections'")
                max_connections = cursor.fetchone()[0]
                cursor.execute(
                    """
                    SELECT count(*)
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                      AND xact_start IS NOT NULL
                      AND now() - xact_start > interval '5 minutes'
                      AND state <> 'idle'
                    """
                )
                long_transactions = cursor.fetchone()[0]
                cursor.execute("SELECT count(*) FROM pg_locks WHERE NOT granted")
                lock_waits = cursor.fetchone()[0]
        except Exception as e:
            logger.warning("Failed to collect PostgreSQL health metrics: %s", e)
            connections = max_connections = long_transactions = lock_waits = 0

        connections_metric.add_metric([], float(connections or 0))
        max_connections_metric.add_metric([], float(max_connections or 0))
        long_transactions_metric.add_metric([], float(long_transactions or 0))
        lock_waits_metric.add_metric([], float(lock_waits or 0))
        yield connections_metric
        yield max_connections_metric
        yield long_transactions_metric
        yield lock_waits_metric

    def _redis_health_metrics(self):
        connected_clients_metric = GaugeMetricFamily(
            "codeplace_redis_connected_clients",
            "Current Redis connected clients from INFO clients.",
        )
        max_clients_metric = GaugeMetricFamily(
            "codeplace_redis_max_clients",
            "Configured Redis maxclients from CONFIG GET maxclients.",
        )
        rejected_connections_metric = GaugeMetricFamily(
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
        except Exception as e:
            logger.warning("Failed to collect Redis health metrics: %s", e)
            connected_clients = max_clients = rejected_connections = 0

        connected_clients_metric.add_metric([], connected_clients)
        max_clients_metric.add_metric([], max_clients)
        rejected_connections_metric.add_metric([], rejected_connections)
        yield connected_clients_metric
        yield max_clients_metric
        yield rejected_connections_metric

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


def register_codeplace_metrics():
    if getattr(register_codeplace_metrics, "_registered", False):
        return
    try:
        REGISTRY.register(CodePlaceCollector())
    except ValueError:
        logger.debug("CodePlace metrics collector is already registered")
    register_codeplace_metrics._registered = True
