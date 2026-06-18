import logging

from utils.shortcuts import get_env

logger = logging.getLogger(__name__)


def configure_opentelemetry(service_name):
    if get_env("OTEL_ENABLED", "0").lower() not in ("1", "true", "yes", "on"):
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.celery import CeleryInstrumentor
        from opentelemetry.instrumentation.django import DjangoInstrumentor
        from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
    except Exception:
        logger.exception("OpenTelemetry packages are unavailable")
        return

    try:
        sampler_ratio = float(get_env("OTEL_TRACES_SAMPLER_ARG", "0.05"))
    except ValueError:
        logger.warning("Invalid OTEL_TRACES_SAMPLER_ARG; falling back to 0.05")
        sampler_ratio = 0.05
    sampler_ratio = min(max(sampler_ratio, 0), 1)
    resource = Resource.create({
        "service.name": service_name,
        "deployment.environment": get_env("OJ_ENV", "dev"),
    })
    provider = TracerProvider(resource=resource, sampler=ParentBased(TraceIdRatioBased(sampler_ratio)))
    endpoint = get_env("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector.monitoring.svc.cluster.local:4317")
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True)))
    trace.set_tracer_provider(provider)

    DjangoInstrumentor().instrument()
    RequestsInstrumentor().instrument()
    Psycopg2Instrumentor().instrument()
    RedisInstrumentor().instrument()
    CeleryInstrumentor().instrument()
