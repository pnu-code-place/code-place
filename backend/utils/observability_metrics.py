import logging
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from prometheus_client import Counter, Histogram, REGISTRY
from prometheus_client.core import GaugeMetricFamily, HistogramMetricFamily

from submission.models import JudgeStatus, Submission
from utils.cache import cache
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


class CodePlaceCollector:

    def describe(self):
        yield GaugeMetricFamily(
            "codeplace_submission_status_count",
            "Current number of submissions grouped by judge status.",
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

    def collect(self):
        yield from self._submission_status_count()
        yield self._waiting_queue_length()
        yield from self._judge_server_metrics()
        yield self._judge_duration_histogram()

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
            hostname = server.hostname or "unknown"
            heartbeat_age = max((now - server.last_heartbeat).total_seconds(), 0)
            available = 1 if not server.is_disabled and server.status == "normal" else 0
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


def register_codeplace_metrics():
    if getattr(register_codeplace_metrics, "_registered", False):
        return
    try:
        REGISTRY.register(CodePlaceCollector())
    except ValueError:
        logger.debug("CodePlace metrics collector is already registered")
    register_codeplace_metrics._registered = True
