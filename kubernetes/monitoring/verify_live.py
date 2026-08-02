#!/usr/bin/env python3
"""Fail fast when the live monitoring stack no longer matches its target contract."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Check:
    name: str
    query: str
    predicate: Callable[[float], bool]
    expectation: str


ONE = lambda value: value == 1  # noqa: E731
POSITIVE = lambda value: value > 0  # noqa: E731
AT_LEAST_TWO = lambda value: value >= 2  # noqa: E731
AT_LEAST_THREE = lambda value: value >= 3  # noqa: E731
AT_LEAST_SIX = lambda value: value >= 6  # noqa: E731

CHECKS = (
    Check("backend dev scrape", 'min(up{job="backend",namespace="code-place-dev"})', ONE, "1"),
    Check(
        "backend dev target coverage",
        'count(up{job="backend",namespace="code-place-dev"})',
        AT_LEAST_TWO,
        ">= 2 targets",
    ),
    Check("backend prod scrape", 'min(up{job="backend",namespace="code-place-prod"})', ONE, "1"),
    Check(
        "backend prod target coverage",
        'count(up{job="backend",namespace="code-place-prod"})',
        AT_LEAST_SIX,
        ">= 6 targets",
    ),
    Check(
        "PostgreSQL dev collector",
        'min(cnpg_collector_up{namespace="code-place-dev",cluster="postgres",job="postgres"})',
        ONE,
        "1",
    ),
    Check(
        "PostgreSQL dev target coverage",
        'count(cnpg_collector_up{namespace="code-place-dev",cluster="postgres",job="postgres"})',
        AT_LEAST_THREE,
        ">= 3 targets",
    ),
    Check(
        "PostgreSQL prod collector",
        'min(cnpg_collector_up{namespace="code-place-prod",cluster="postgres",job="postgres"})',
        ONE,
        "1",
    ),
    Check(
        "PostgreSQL prod target coverage",
        'count(cnpg_collector_up{namespace="code-place-prod",cluster="postgres",job="postgres"})',
        AT_LEAST_THREE,
        ">= 3 targets",
    ),
    Check("Redis dev exporter", 'min(redis_up{namespace="code-place-dev",job="redis"})', ONE, "1"),
    Check(
        "Redis dev target coverage",
        'count(redis_up{namespace="code-place-dev",job="redis"})',
        AT_LEAST_SIX,
        ">= 6 targets",
    ),
    Check("Redis prod exporter", 'min(redis_up{namespace="code-place-prod",job="redis"})', ONE, "1"),
    Check(
        "Redis prod target coverage",
        'count(redis_up{namespace="code-place-prod",job="redis"})',
        AT_LEAST_SIX,
        ">= 6 targets",
    ),
    Check("Traefik scrape", 'min(up{job="traefik",namespace="kube-system"})', ONE, "1"),
    Check(
        "Traefik request metrics",
        'count(traefik_service_requests_total{job="traefik",namespace="kube-system"})',
        POSITIVE,
        "> 0 series",
    ),
    Check("Alloy scrape", 'min(up{namespace="monitoring",job=~".*alloy.*"})', ONE, "1"),
    Check(
        "Alloy node coverage",
        'min(kube_daemonset_status_number_available{namespace="monitoring",daemonset="alloy"}'
        ' == bool on(namespace,daemonset) '
        'kube_daemonset_status_desired_number_scheduled{namespace="monitoring",daemonset="alloy"})',
        ONE,
        "1",
    ),
    Check(
        "Alloy scheduled nodes",
        'kube_daemonset_status_desired_number_scheduled{namespace="monitoring",daemonset="alloy"}',
        POSITIVE,
        "> 0 nodes",
    ),
    Check("Loki scrape", 'min(up{namespace="monitoring",job=~".*loki$"})', ONE, "1"),
    Check(
        "Longhorn scrape",
        'min(up{namespace="longhorn-system",endpoint="manager"})',
        ONE,
        "1",
    ),
    Check(
        "Kubernetes event exporter scrape",
        'min(up{namespace="monitoring",job="kubernetes-event-exporter"})',
        ONE,
        "1",
    ),
    Check(
        "kube-state-metrics scrape",
        'min(up{namespace="monitoring",service=~".*kube-state-metrics.*"})',
        ONE,
        "1",
    ),
    Check("OTel collector scrape", 'min(up{namespace="monitoring",job="otel-collector"})', ONE, "1"),
    Check(
        "OTel collector target coverage",
        'count(up{namespace="monitoring",job="otel-collector"})',
        AT_LEAST_TWO,
        ">= 2 targets",
    ),
    Check(
        "OTel span metric family",
        'count(otelcol_receiver_accepted_spans_total{namespace="monitoring"})',
        POSITIVE,
        "> 0 series",
    ),
    Check("Tempo scrape", 'min(up{namespace="monitoring",job="tempo"})', ONE, "1"),
    Check("vLLM scrape", 'min(up{namespace="code-place-prod",job="vllm"})', ONE, "1"),
    Check(
        "vLLM request metric family",
        'count({__name__="vllm:num_requests_running",namespace="code-place-prod"})',
        POSITIVE,
        "> 0 series",
    ),
    Check("DCGM scrape", 'min(up{namespace="monitoring",job="dcgm-exporter"})', ONE, "1"),
    Check(
        "DCGM GPU metric family",
        'count(DCGM_FI_DEV_GPU_UTIL{namespace="monitoring"})',
        POSITIVE,
        "> 0 series",
    ),
    Check(
        "Blackbox exporter scrape",
        'min(up{namespace="monitoring",job="blackbox-exporter"})',
        ONE,
        "1",
    ),
    Check(
        "Blackbox exporter target coverage",
        'count(up{namespace="monitoring",job="blackbox-exporter"})',
        AT_LEAST_TWO,
        ">= 2 targets",
    ),
    Check(
        "Prometheus ready replicas",
        'sum(kube_pod_status_ready{namespace="monitoring",condition="true",'
        'pod=~"prometheus-kube-prometheus-stack-prometheus-.*"})',
        AT_LEAST_TWO,
        ">= 2",
    ),
    Check(
        "Alertmanager ready replicas",
        'sum(kube_pod_status_ready{namespace="monitoring",condition="true",'
        'pod=~"alertmanager-kube-prometheus-stack-alertmanager-.*"})',
        AT_LEAST_TWO,
        ">= 2",
    ),
    Check(
        "Prometheus Alertmanager discovery",
        'min(prometheus_notifications_alertmanagers_discovered{'
        'namespace="monitoring",job="kube-prometheus-stack-prometheus"})',
        POSITIVE,
        ">= 1 per Prometheus replica",
    ),
    Check(
        "Alertmanager configuration reload",
        'min(alertmanager_config_last_reload_successful{'
        'namespace="monitoring",job="kube-prometheus-stack-alertmanager"})',
        ONE,
        "1",
    ),
    Check(
        "dev frontend public probe",
        'min(probe_success{environment="dev",namespace="code-place-dev",service="frontend",probe_type="public-http"})',
        ONE,
        "1",
    ),
    Check(
        "dev hub-auth public probe",
        'min(probe_success{environment="dev",namespace="code-place-dev",service="hub-auth",probe_type="public-http"})',
        ONE,
        "1",
    ),
    Check(
        "prod frontend public probe",
        'min(probe_success{environment="prod",namespace="code-place-prod",service="frontend",probe_type="public-http"})',
        ONE,
        "1",
    ),
    Check(
        "prod hub-auth public probe",
        'min(probe_success{environment="prod",namespace="code-place-prod",service="hub-auth",probe_type="public-http"})',
        ONE,
        "1",
    ),
    Check(
        "Grafana public probe",
        'min(probe_success{environment="monitoring",namespace="monitoring",service="grafana",probe_type="public-http"})',
        ONE,
        "1",
    ),
    Check("dev custom collectors", 'min(codeplace_collector_success{namespace="code-place-dev"})', ONE, "1"),
    Check(
        "dev collector replica coverage",
        'count(codeplace_collector_success{namespace="code-place-dev"}) >= bool 8',
        ONE,
        "4 collector series x 2 expected backend targets",
    ),
    Check("dev Sentinel health", 'min(codeplace_redis_sentinel_health{namespace="code-place-dev"})', ONE, "1"),
    Check(
        "dev Sentinel replica coverage",
        'count(codeplace_redis_sentinel_health{namespace="code-place-dev"}) >= bool 4',
        ONE,
        "2 Sentinel check series x 2 expected backend targets",
    ),
    Check("prod custom collectors", 'min(codeplace_collector_success{namespace="code-place-prod"})', ONE, "1"),
    Check(
        "prod collector replica coverage",
        'count(codeplace_collector_success{namespace="code-place-prod"}) >= bool 24',
        ONE,
        "4 collector series x 6 expected backend targets",
    ),
    Check("prod Sentinel health", 'min(codeplace_redis_sentinel_health{namespace="code-place-prod"})', ONE, "1"),
    Check(
        "prod Sentinel replica coverage",
        'count(codeplace_redis_sentinel_health{namespace="code-place-prod"}) >= bool 12',
        ONE,
        "2 Sentinel check series x 6 expected backend targets",
    ),
)


def query(prometheus_url: str, expression: str, timeout: float) -> float:
    params = urllib.parse.urlencode({"query": expression})
    url = f"{prometheus_url.rstrip('/')}/api/v1/query?{params}"
    with urllib.request.urlopen(url, timeout=timeout) as response:
        payload = json.load(response)
    if payload.get("status") != "success":
        raise RuntimeError(payload.get("error") or "Prometheus returned a failed response")
    result = payload.get("data", {}).get("result", [])
    if len(result) != 1:
        raise RuntimeError(f"expected one result series, got {len(result)}")
    return float(result[0]["value"][1])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prometheus-url", default="http://127.0.0.1:9090")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    failures = 0
    for check in CHECKS:
        try:
            value = query(args.prometheus_url, check.query, args.timeout)
        except Exception as exc:  # One failed query must not hide the remaining contract failures.
            failures += 1
            print(f"FAIL {check.name}: {exc}")
            continue
        if check.predicate(value):
            print(f"PASS {check.name}: {value:g}")
        else:
            failures += 1
            print(f"FAIL {check.name}: got {value:g}, expected {check.expectation}")

    if failures:
        print(f"\n{failures} live monitoring contract check(s) failed.", file=sys.stderr)
        return 1
    print("\nAll live monitoring contracts passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
