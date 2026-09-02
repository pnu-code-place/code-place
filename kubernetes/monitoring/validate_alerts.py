#!/usr/bin/env python3
"""Validate public endpoint alerts and their notification routing."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent


def load_yaml(name: str) -> dict[str, Any]:
    return yaml.safe_load((ROOT / name).read_text(encoding="utf-8"))


def load_yaml_documents(name: str) -> list[dict[str, Any]]:
    return [
        document
        for document in yaml.safe_load_all((ROOT / name).read_text(encoding="utf-8"))
        if document is not None
    ]


def main() -> int:
    prometheus = load_yaml("prometheus-rules.yaml")
    alertmanager = load_yaml("alertmanager-config.yaml")
    datastore_monitors = load_yaml_documents("datastore-pod-monitors.yaml")
    rules = [
        rule
        for group in prometheus["spec"]["groups"]
        for rule in group.get("rules", [])
        if "alert" in rule
    ]
    errors: list[str] = []

    for rule in rules:
        annotations = rule.get("annotations", {})
        for field in ("summary", "description"):
            value = annotations.get(field, "")
            if not value:
                errors.append(f"{rule['alert']}: missing {field} annotation")
            elif not any("가" <= character <= "힣" for character in value):
                errors.append(f"{rule['alert']}: {field} annotation must be Korean")

    postgres_monitors = [
        monitor
        for monitor in datastore_monitors
        if monitor.get("kind") == "PodMonitor"
        and monitor.get("metadata", {}).get("name") == "postgres"
    ]
    if len(postgres_monitors) != 1:
        errors.append("expected exactly one PostgreSQL PodMonitor")
    else:
        endpoints = postgres_monitors[0].get("spec", {}).get("podMetricsEndpoints", [])
        relabelings = endpoints[0].get("relabelings", []) if len(endpoints) == 1 else []
        if not any(
            relabeling.get("sourceLabels")
            == ["__meta_kubernetes_pod_label_cnpg_io_cluster"]
            and relabeling.get("targetLabel") == "cluster"
            for relabeling in relabelings
        ):
            errors.append("PostgreSQL PodMonitor must expose the CNPG cluster label")

    expected_environments = {
        "code-place-prod": ("prod", "P0", "1m"),
        "code-place-dev": ("dev", "P1", "2m"),
    }

    endpoint_rules = [rule for rule in rules if rule["alert"] == "PublicEndpointDown"]
    if len(endpoint_rules) != 2:
        errors.append(f"expected two PublicEndpointDown rules, found {len(endpoint_rules)}")
    for namespace, (environment, priority, duration) in expected_environments.items():
        matching = [rule for rule in endpoint_rules if rule.get("labels", {}).get("namespace") == namespace]
        if len(matching) != 1:
            errors.append(f"{namespace}: expected exactly one PublicEndpointDown rule")
            continue
        rule = matching[0]
        expression = rule["expr"]
        for token in (
            f'environment="{environment}"',
            f'namespace="{namespace}"',
            'probe_type="public-http"',
            'service=~"frontend|hub-auth"',
        ):
            if token not in expression:
                errors.append(f"{namespace}: PublicEndpointDown is missing {token}")
        if "absent(" in expression:
            errors.append(f"{namespace}: PublicEndpointDown must not treat missing telemetry as downtime")
        if rule.get("labels", {}).get("priority") != priority:
            errors.append(f"{namespace}: PublicEndpointDown priority must be {priority}")
        if rule.get("for") != duration:
            errors.append(f"{namespace}: PublicEndpointDown must persist for {duration}")
        annotations = rule.get("annotations", {})
        if "$labels.service" not in annotations.get("summary", ""):
            errors.append(f"{namespace}: PublicEndpointDown summary must identify the service")
        if "$labels.instance" not in annotations.get("description", ""):
            errors.append(f"{namespace}: PublicEndpointDown description must identify the instance")

    missing_rules = [rule for rule in rules if rule["alert"] == "PublicEndpointProbeMissing"]
    if len(missing_rules) != 2:
        errors.append(f"expected two PublicEndpointProbeMissing rules, found {len(missing_rules)}")
    for namespace, (environment, _, _) in expected_environments.items():
        matching = [rule for rule in missing_rules if rule.get("labels", {}).get("namespace") == namespace]
        if len(matching) != 1:
            errors.append(f"{namespace}: expected exactly one PublicEndpointProbeMissing rule")
            continue
        rule = matching[0]
        expression = rule["expr"]
        if expression.count("absent(") != 2:
            errors.append(f"{namespace}: probe coverage must check frontend and hub-auth separately")
        for service in ("frontend", "hub-auth"):
            expected = (
                f'absent(probe_success{{environment="{environment}", namespace="{namespace}", '
                f'service="{service}", probe_type="public-http"}})'
            )
            if expected not in expression:
                errors.append(f"{namespace}: missing {service} probe coverage check")
        if rule.get("labels", {}).get("priority") != "P1":
            errors.append(f"{namespace}: missing probe telemetry must be reported separately as P1")
        if rule.get("for") != "2m":
            errors.append(f"{namespace}: missing probe telemetry must persist for 2m")

    scrape_coverage_contracts = (
        (
            "BackendTargetDown",
            "code-place-dev",
            'count(up{job="backend", namespace="code-place-dev"}) < 2',
        ),
        (
            "BackendTargetDown",
            "code-place-prod",
            'count(up{job="backend", namespace="code-place-prod"}) < 6',
        ),
        (
            "CodePlaceTelemetryCoverageIncomplete",
            "code-place-dev",
            'count(codeplace_collector_success{namespace="code-place-dev"}) < 8',
        ),
        (
            "CodePlaceTelemetryCoverageIncomplete",
            "code-place-dev",
            'count(codeplace_redis_sentinel_health{namespace="code-place-dev"}) < 4',
        ),
        (
            "CodePlaceTelemetryCoverageIncomplete",
            "code-place-prod",
            'count(codeplace_collector_success{namespace="code-place-prod"}) < 24',
        ),
        (
            "CodePlaceTelemetryCoverageIncomplete",
            "code-place-prod",
            'count(codeplace_redis_sentinel_health{namespace="code-place-prod"}) < 12',
        ),
        (
            "PostgresCollectorUnavailable",
            "code-place-dev",
            'count(cnpg_collector_up{namespace="code-place-dev", cluster="postgres"}) < 3',
        ),
        (
            "PostgresCollectorUnavailable",
            "code-place-prod",
            'count(cnpg_collector_up{namespace="code-place-prod", cluster="postgres"}) < 3',
        ),
        (
            "RedisExporterCoverageIncomplete",
            "code-place-dev",
            'count(redis_up{namespace="code-place-dev", job="redis"}) < 6',
        ),
        (
            "RedisExporterCoverageIncomplete",
            "code-place-prod",
            'count(redis_up{namespace="code-place-prod", job="redis"}) < 6',
        ),
        (
            "OpenTelemetryCollectorUnavailable",
            "monitoring",
            'count(up{job="otel-collector", namespace="monitoring"}) < 2',
        ),
        (
            "BlackboxExporterCoverageIncomplete",
            "monitoring",
            'count(up{job="blackbox-exporter", namespace="monitoring"}) < 2',
        ),
    )
    for alert_name, namespace, expected_expression in scrape_coverage_contracts:
        matching = [
            rule
            for rule in rules
            if rule["alert"] == alert_name
            and rule.get("labels", {}).get("namespace") == namespace
        ]
        if len(matching) != 1:
            errors.append(f"{namespace}: expected exactly one {alert_name} rule")
        elif expected_expression not in matching[0]["expr"]:
            errors.append(
                f"{namespace}: {alert_name} must enforce expected target coverage"
            )

    target_context_contracts = (
        (
            "TraefikScrapeUnavailable",
            "kube-system",
            'up{job="traefik", namespace="kube-system"} == 0',
            "traefik",
        ),
        (
            "AlloyScrapeUnavailable",
            "monitoring",
            'up{job=~".*alloy.*", namespace="monitoring"} == 0',
            "alloy",
        ),
        (
            "BackendTargetDown",
            "code-place-dev",
            'up{job="backend", namespace="code-place-dev"} == 0',
            "backend",
        ),
        (
            "BackendTargetDown",
            "code-place-prod",
            'up{job="backend", namespace="code-place-prod"} == 0',
            "backend",
        ),
        (
            "RedisSentinelUnavailable",
            "code-place-dev",
            'codeplace_redis_sentinel_health{namespace="code-place-dev"} == 0',
            "redis",
        ),
        (
            "RedisSentinelUnavailable",
            "code-place-prod",
            'codeplace_redis_sentinel_health{namespace="code-place-prod"} == 0',
            "redis",
        ),
        (
            "CodePlaceCollectorFailed",
            "code-place-dev",
            'codeplace_collector_success{namespace="code-place-dev"} == 0',
            "backend",
        ),
        (
            "CodePlaceCollectorFailed",
            "code-place-prod",
            'codeplace_collector_success{namespace="code-place-prod"} == 0',
            "backend",
        ),
        (
            "PostgresCollectorUnavailable",
            "code-place-dev",
            'cnpg_collector_up{namespace="code-place-dev", cluster="postgres"} == 0',
            "postgres",
        ),
        (
            "PostgresCollectorUnavailable",
            "code-place-prod",
            'cnpg_collector_up{namespace="code-place-prod", cluster="postgres"} == 0',
            "postgres",
        ),
        (
            "RedisExporterCoverageIncomplete",
            "code-place-dev",
            'redis_up{namespace="code-place-dev", job="redis"} == 0',
            "redis",
        ),
        (
            "RedisExporterCoverageIncomplete",
            "code-place-prod",
            'redis_up{namespace="code-place-prod", job="redis"} == 0',
            "redis",
        ),
        (
            "OpenTelemetryCollectorUnavailable",
            "monitoring",
            'up{job="otel-collector", namespace="monitoring"} == 0',
            "otel-collector",
        ),
        (
            "BlackboxExporterCoverageIncomplete",
            "monitoring",
            'up{job="blackbox-exporter", namespace="monitoring"} == 0',
            "blackbox-exporter",
        ),
    )
    for alert_name, namespace, expected_expression, service in target_context_contracts:
        matching = [
            rule
            for rule in rules
            if rule["alert"] == alert_name
            and rule.get("labels", {}).get("namespace") == namespace
        ]
        if len(matching) != 1:
            errors.append(f"{namespace}: expected exactly one {alert_name} rule")
            continue
        rule = matching[0]
        if expected_expression not in rule["expr"]:
            errors.append(f"{namespace}: {alert_name} must preserve failed target labels")
        if rule.get("labels", {}).get("service") != service:
            errors.append(f"{namespace}: {alert_name} must identify service {service}")

    group_by = alertmanager["spec"]["route"].get("groupBy", [])
    if "service" not in group_by:
        errors.append("Alertmanager must group endpoint notifications by service")

    routes = alertmanager["spec"]["route"].get("routes", [])
    expected_routes = (
        ({"priority": "P0"}, "p0-discord"),
        ({"priority": "P1", "namespace": "code-place-dev"}, "dev-p1-muted"),
        ({"priority": "P1"}, "p1-discord"),
        ({"severity": "critical"}, "p0-discord"),
        ({"severity": "warning", "namespace": "code-place-dev"}, "dev-p1-muted"),
        ({"severity": "warning"}, "p1-discord"),
    )
    previous_index = -1
    for expected_matchers, expected_receiver in expected_routes:
        matching_indexes = [
            index
            for index, route in enumerate(routes)
            if {
                matcher.get("name"): matcher.get("value")
                for matcher in route.get("matchers", [])
            }
            == expected_matchers
            and route.get("receiver") == expected_receiver
        ]
        if len(matching_indexes) != 1:
            errors.append(
                f"Alertmanager must route {expected_matchers} to {expected_receiver} exactly once"
            )
            continue
        if matching_indexes[0] <= previous_index:
            errors.append("Alertmanager priority routes must precede severity fallback routes")
        previous_index = matching_indexes[0]

    receivers = {receiver["name"]: receiver for receiver in alertmanager["spec"]["receivers"]}
    for receiver_name, priority in (("p0-discord", "P0"), ("p1-discord", "P1")):
        configs = receivers.get(receiver_name, {}).get("discordConfigs", [])
        if len(configs) != 1:
            errors.append(f"{receiver_name}: expected exactly one Discord config")
            continue
        config = configs[0]
        title = config.get("title", "")
        message = config.get("message", "")
        if ".CommonLabels.service" not in title:
            errors.append(f"{receiver_name}: title must identify the failed service")
        if ".CommonAnnotations.summary" not in title:
            errors.append(f"{receiver_name}: title must use the Korean alert summary")
        if "활성" not in title:
            errors.append(f"{receiver_name}: repeated firing notifications must use the active-state label")
        for token in (
            ".Labels.service",
            ".Labels.instance",
            ".Labels.pod",
            ".Labels.container",
            ".Labels.persistentvolumeclaim",
            ".Labels.pvc",
            ".Labels.pvc_namespace",
            ".Labels.deployment",
            ".Labels.daemonset",
            ".Labels.node",
            ".Labels.volume",
            ".Labels.disk",
            ".Labels.reason",
            ".Labels.condition",
            ".Labels.collector",
            ".Labels.check",
            ".Labels.scope",
            ".Labels.status",
            ".Labels.Hostname",
            ".Labels.gpu",
            ".Labels.UUID",
            ".Annotations.description",
            ".Annotations.summary",
        ):
            if token not in message:
                errors.append(f"{receiver_name}: message is missing {token}")
        if "문맥:" not in message:
            errors.append(f"{receiver_name}: message must show available workload context labels")
        if message.count(".GeneratorURL") != 1:
            errors.append(f"{receiver_name}: message must show one query link per alert group")
        if "발생 쿼리: [Prometheus에서 보기]" not in message:
            errors.append(f"{receiver_name}: query URL must use a compact link label")
        if f"우선순위: {priority}" not in message:
            errors.append(f"{receiver_name}: message must show its routed priority {priority}")
        for environment in ("prod", "dev"):
            storage_link = (
                f"스토리지({environment}): "
                "https://monitoring.code-place-dev.kr/d/codeplace-storage/"
                f"codeplace-storage?orgId=1&var-environment={environment}"
            )
            if storage_link not in message:
                errors.append(
                    f"{receiver_name}: Longhorn message is missing the {environment} storage link"
                )

    if errors:
        print("Monitoring alert validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Validated endpoint separation, scrape coverage, notification context, "
        "routing, and dashboard links."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
