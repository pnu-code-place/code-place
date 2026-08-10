#!/usr/bin/env python3
"""Validate the contracts shared by the provisioned CodePlace dashboards."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
ENVIRONMENT_DASHBOARDS = {
    "codeplace-overview",
    "codeplace-platform",
    "codeplace-logs",
    "codeplace-kubernetes-events",
    "codeplace-ai-api",
    "codeplace-public-endpoints",
    "codeplace-storage",
    "codeplace-traces",
}
PRODUCTION_ONLY_DASHBOARDS = {"codeplace-ai-inference"}
GLOBAL_DASHBOARDS = {"codeplace-log-pipeline", "codeplace-monitoring-stack"}
MIXED_ENVIRONMENT_PATTERNS = (
    'code-place-(dev|prod)',
    'code-place-(prod|dev)',
    'code-place-dev|code-place-prod',
    'code-place-prod|code-place-dev',
)


def embedded_json_documents(path: Path) -> Iterable[dict[str, Any]]:
    """Extract JSON literal blocks from the dashboard ConfigMap without PyYAML."""
    lines = path.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        match = re.match(r"^  ([^:]+\.json):\s*\|[-+]?\s*$", lines[index])
        if not match:
            index += 1
            continue

        key = match.group(1)
        index += 1
        block: list[str] = []
        while index < len(lines) and (not lines[index] or lines[index].startswith("    ")):
            block.append(lines[index][4:] if lines[index].startswith("    ") else "")
            index += 1
        try:
            yield json.loads("\n".join(block))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{key}: invalid embedded JSON: {exc}") from exc


def all_panels(panels: Iterable[dict[str, Any]]) -> Iterable[dict[str, Any]]:
    for panel in panels:
        yield panel
        yield from all_panels(panel.get("panels", []))


def all_query_text(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"expr", "query"} and isinstance(child, str):
                yield child
            yield from all_query_text(child)
    elif isinstance(value, list):
        for child in value:
            yield from all_query_text(child)


def validate_environment_variable(dashboard: dict[str, Any], errors: list[str]) -> None:
    uid = dashboard["uid"]
    variables = dashboard.get("templating", {}).get("list", [])
    environment = [variable for variable in variables if variable.get("name") == "environment"]
    if len(environment) != 1:
        errors.append(f"{uid}: expected exactly one environment variable")
        return

    variable = environment[0]
    expected = {
        "type": "custom",
        "query": "prod,dev",
        "includeAll": False,
        "multi": False,
    }
    for key, value in expected.items():
        if variable.get(key) != value:
            errors.append(f"{uid}: environment.{key} must be {value!r}")
    if variable.get("current", {}).get("value") != "prod":
        errors.append(f"{uid}: environment must default to prod")


def validate_grid(dashboard: dict[str, Any], errors: list[str]) -> None:
    uid = dashboard["uid"]
    rectangles: list[tuple[int, int, int, int, str]] = []
    for panel in all_panels(dashboard.get("panels", [])):
        if panel.get("type") == "row":
            continue
        position = panel.get("gridPos")
        if not isinstance(position, dict):
            errors.append(f"{uid}: panel {panel.get('title')!r} has no gridPos")
            continue
        try:
            x, y, width, height = (int(position[key]) for key in ("x", "y", "w", "h"))
        except (KeyError, TypeError, ValueError):
            errors.append(f"{uid}: panel {panel.get('title')!r} has an invalid gridPos")
            continue
        if x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > 24:
            errors.append(f"{uid}: panel {panel.get('title')!r} is outside the 24-column grid")
        rectangles.append((x, y, x + width, y + height, str(panel.get("title"))))

    for index, first in enumerate(rectangles):
        for second in rectangles[index + 1 :]:
            overlaps = first[0] < second[2] and second[0] < first[2] and first[1] < second[3] and second[1] < first[3]
            if overlaps:
                errors.append(f"{uid}: panels {first[4]!r} and {second[4]!r} overlap")


def validate_visualizations(dashboard: dict[str, Any], errors: list[str]) -> None:
    """Keep current-state cards and historical graphs visually unambiguous."""
    uid = dashboard["uid"]
    for panel in all_panels(dashboard.get("panels", [])):
        panel_type = panel.get("type")
        title = panel.get("title")
        if panel_type == "stat":
            if panel.get("options", {}).get("graphMode") != "none":
                errors.append(f"{uid}: stat panel {title!r} must not render a sparkline")
            if panel.get("datasource") == "Prometheus":
                for target in panel.get("targets", []):
                    if target.get("expr") and target.get("instant") is not True:
                        errors.append(
                            f"{uid}: stat panel {title!r} must query the current instant"
                        )
            continue
        if panel_type != "timeseries":
            continue

        field_config = panel.get("fieldConfig", {})
        defaults = field_config.get("defaults", {})
        custom = defaults.get("custom", {})
        draw_style = custom.get("drawStyle")
        if draw_style not in {"line", "bars"}:
            errors.append(f"{uid}: timeseries panel {title!r} must explicitly use lines or bars")
            continue
        if custom.get("showPoints") not in {"auto", "always", "never"}:
            errors.append(f"{uid}: timeseries panel {title!r} must explicitly configure points")
        if draw_style == "line" and custom.get("lineWidth", 0) <= 0:
            errors.append(f"{uid}: line panel {title!r} must have a visible line width")
        if draw_style == "bars" and "barAlignment" not in custom:
            errors.append(f"{uid}: bar panel {title!r} must explicitly align its bars")

        threshold_steps = defaults.get("thresholds", {}).get("steps", [])
        if len(threshold_steps) > 1:
            if custom.get("thresholdsStyle", {}).get("mode") != "line":
                errors.append(f"{uid}: threshold panel {title!r} must show threshold lines")
            allows_negative = (
                uid == "codeplace-public-endpoints"
                and str(title).endswith("TLS Days Left")
            )
            if defaults.get("min") != 0 and not allows_negative:
                errors.append(f"{uid}: threshold panel {title!r} must start at zero")
            expected_max = {"percentunit": 1, "percent": 100}.get(defaults.get("unit"))
            if expected_max is not None and defaults.get("max") != expected_max:
                errors.append(
                    f"{uid}: bounded threshold panel {title!r} must end at {expected_max}"
                )

        for override in field_config.get("overrides", []):
            properties = {
                prop.get("id"): prop.get("value")
                for prop in override.get("properties", [])
            }
            if "unit" in properties and properties["unit"] != defaults.get("unit"):
                if properties.get("custom.axisPlacement") != "right":
                    errors.append(
                        f"{uid}: mixed-unit panel {title!r} must place the override on the right axis"
                    )


def validate_operational_semantics(dashboard: dict[str, Any], errors: list[str]) -> None:
    """Guard the small set of panels whose colors directly communicate health."""
    uid = dashboard["uid"]
    panels = list(all_panels(dashboard.get("panels", [])))

    if uid in {"codeplace-overview", "codeplace-ai-api"}:
        expressions = [
            target.get("expr", "")
            for panel in panels
            for target in panel.get("targets", [])
            if 'up{job="backend"' in target.get("expr", "")
        ]
        if len(expressions) != 1:
            errors.append(f"{uid}: expected one backend health expression")
        else:
            expression = expressions[0]
            for token in (
                "sum by (namespace)",
                "kube_deployment_spec_replicas",
                ">= bool",
                "or on() vector(0)",
            ):
                if token not in expression:
                    errors.append(f"{uid}: backend health must enforce desired replicas with {token}")

    if uid == "codeplace-public-endpoints":
        matching = [panel for panel in panels if panel.get("title", "").endswith("HTTP Status")]
        if len(matching) != 1:
            errors.append(f"{uid}: expected one HTTP status panel")
        else:
            steps = matching[0].get("fieldConfig", {}).get("defaults", {}).get(
                "thresholds", {}
            ).get("steps", [])
            if steps != [
                {"color": "red", "value": None},
                {"color": "green", "value": 200},
                {"color": "red", "value": 201},
            ]:
                errors.append(f"{uid}: HTTP status colors must accept only status 200")


def validate_shared_judge_outcome(dashboard: dict[str, Any], errors: list[str]) -> None:
    """A Redis-backed counter is exposed identically by every backend replica."""
    expressions = [
        expression
        for expression in all_query_text(dashboard)
        if "codeplace_judge_task_outcome_total" in expression
    ]
    for expression in expressions:
        if not expression.startswith("avg by (namespace, scope, status) (rate("):
            errors.append(
                f"{dashboard['uid']}: shared judge outcome rate must be averaged across backend replicas"
            )


def validate_alert_delivery_visibility(dashboard: dict[str, Any], errors: list[str]) -> None:
    if dashboard["uid"] != "codeplace-monitoring-stack":
        return
    query_text = "\n".join(all_query_text(dashboard))
    for metric in (
        "alertmanager-kube-prometheus-stack-alertmanager-",
        "prometheus_notifications_alertmanagers_discovered",
        "alertmanager_config_last_reload_successful",
        "alertmanager_notifications_failed_total",
    ):
        if metric not in query_text:
            errors.append(f"{dashboard['uid']}: alert delivery visibility is missing {metric}")


def validate_scrape_target_coverage(dashboard: dict[str, Any], errors: list[str]) -> None:
    """Fixed-replica targets must not look healthy when discovery is partial."""
    if dashboard["uid"] != "codeplace-monitoring-stack":
        return

    panels = {panel.get("title"): panel for panel in all_panels(dashboard.get("panels", []))}
    expected_panel = panels.get("Expected scrape targets", {})
    target_expressions = {
        target.get("legendFormat"): target.get("expr", "")
        for target in expected_panel.get("targets", [])
    }
    expected_counts = {
        "backend dev": 'count(up{job="backend", namespace="code-place-dev"}) >= bool 2',
        "backend prod": 'count(up{job="backend", namespace="code-place-prod"}) >= bool 6',
        "postgres dev": 'count(up{job="postgres", namespace="code-place-dev"}) >= bool 3',
        "postgres prod": 'count(up{job="postgres", namespace="code-place-prod"}) >= bool 3',
        "redis dev": 'count(up{job="redis", namespace="code-place-dev"}) >= bool 6',
        "redis prod": 'count(up{job="redis", namespace="code-place-prod"}) >= bool 6',
        "OTel Collector": 'count(up{job="otel-collector", namespace="monitoring"}) >= bool 2',
        "Blackbox exporter": 'count(up{job="blackbox-exporter", namespace="monitoring"}) >= bool 2',
    }
    for legend, expected_expression in expected_counts.items():
        expression = target_expressions.get(legend, "")
        if expected_expression not in expression:
            errors.append(
                f"{dashboard['uid']}: {legend} must enforce expected target coverage"
            )

    coverage_panel = panels.get("Application telemetry coverage", {})
    coverage_expressions = {
        target.get("legendFormat"): target.get("expr", "")
        for target in coverage_panel.get("targets", [])
    }
    expected_denominators = {
        "custom collectors dev (4 x 2 replicas)": "/ 8",
        "custom collectors prod (4 x 6 replicas)": "/ 24",
        "Sentinel checks dev (2 x 2 replicas)": "/ 4",
        "Sentinel checks prod (2 x 6 replicas)": "/ 12",
    }
    for legend, denominator in expected_denominators.items():
        expression = coverage_expressions.get(legend, "")
        if denominator not in expression or not expression.startswith("clamp_max("):
            errors.append(
                f"{dashboard['uid']}: {legend} must use the expected deployment coverage"
            )
        if 'count(up{job="backend"' in expression:
            errors.append(
                f"{dashboard['uid']}: {legend} must not derive expected coverage from discovered targets"
            )


def validate_navigation(dashboard: dict[str, Any], errors: list[str]) -> None:
    """Keep signal dashboards discoverable without losing variables or time range."""
    uid = dashboard["uid"]
    if "codeplace" not in dashboard.get("tags", []):
        errors.append(f"{uid}: dashboard must carry the codeplace navigation tag")
    links = dashboard.get("links", [])
    matching = [
        link
        for link in links
        if link.get("type") == "dashboards"
        and link.get("title") == "CodePlace Dashboards"
    ]
    if len(matching) != 1:
        errors.append(f"{uid}: expected one CodePlace dashboard navigation link")
        return

    link = matching[0]
    for key, expected in (
        ("asDropdown", True),
        ("includeVars", True),
        ("keepTime", True),
        ("targetBlank", False),
    ):
        if link.get(key) is not expected:
            errors.append(f"{uid}: navigation.{key} must be {expected!r}")
    if "codeplace" not in link.get("tags", []):
        errors.append(f"{uid}: navigation must filter on the codeplace tag")


def validate_dashboard(dashboard: dict[str, Any], errors: list[str]) -> None:
    uid = dashboard.get("uid")
    if not isinstance(uid, str) or not uid:
        errors.append("dashboard is missing a stable uid")
        return
    if not dashboard.get("title") or not isinstance(dashboard.get("panels"), list):
        errors.append(f"{uid}: title or panels are missing")
    if dashboard.get("refresh") not in {"30s", "1m"}:
        errors.append(f"{uid}: refresh must be 30s or 1m")

    known_scope = ENVIRONMENT_DASHBOARDS | PRODUCTION_ONLY_DASHBOARDS | GLOBAL_DASHBOARDS
    if uid not in known_scope:
        errors.append(f"{uid}: dashboard environment scope is not declared")

    if uid in ENVIRONMENT_DASHBOARDS:
        validate_environment_variable(dashboard, errors)

    if uid in PRODUCTION_ONLY_DASHBOARDS:
        variables = dashboard.get("templating", {}).get("list", [])
        if any(variable.get("name") == "environment" for variable in variables):
            errors.append(f"{uid}: production-only dashboard must not have an environment selector")

    if uid in GLOBAL_DASHBOARDS:
        variables = dashboard.get("templating", {}).get("list", [])
        if any(variable.get("name") == "environment" for variable in variables):
            errors.append(f"{uid}: global dashboard must not have an environment selector")

    query_text = "\n".join(all_query_text(dashboard))
    if "$namespace" in query_text:
        errors.append(f"{uid}: legacy $namespace query remains")
    for pattern in MIXED_ENVIRONMENT_PATTERNS:
        if pattern in query_text:
            errors.append(f"{uid}: mixed-environment query remains: {pattern}")
    if uid in PRODUCTION_ONLY_DASHBOARDS and "code-place-dev" in query_text:
        errors.append(f"{uid}: production-only dashboard contains a dev query")

    validate_grid(dashboard, errors)
    validate_visualizations(dashboard, errors)
    validate_operational_semantics(dashboard, errors)
    validate_shared_judge_outcome(dashboard, errors)
    validate_alert_delivery_visibility(dashboard, errors)
    validate_scrape_target_coverage(dashboard, errors)
    validate_navigation(dashboard, errors)


def prometheus_rules(dashboards: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Build a native Prometheus rule file so promtool can parse dashboard PromQL."""
    rules: list[dict[str, str]] = []
    for dashboard in dashboards:
        for panel in all_panels(dashboard.get("panels", [])):
            if panel.get("datasource") != "Prometheus":
                continue
            for target in panel.get("targets", []):
                expression = target.get("expr")
                if not isinstance(expression, str) or not expression:
                    continue
                rules.append({
                    "record": f"dashboard_contract:expression_{len(rules)}",
                    "expr": expression.replace("$environment", "prod"),
                })
    return {"groups": [{"name": "dashboard.contract", "rules": rules}]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prometheus-rules-output",
        type=Path,
        help="write dashboard PromQL as a native rule file for promtool",
    )
    args = parser.parse_args()

    errors: list[str] = []
    dashboard_count = 0
    dashboards: list[dict[str, Any]] = []
    seen_uids: set[str] = set()
    for path in sorted(ROOT.glob("grafana-dashboard-*.yaml")):
        try:
            documents = list(embedded_json_documents(path))
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not documents:
            errors.append(f"{path.name}: no embedded dashboard JSON found")
        for dashboard in documents:
            dashboard_count += 1
            dashboards.append(dashboard)
            uid = dashboard.get("uid")
            if uid in seen_uids:
                errors.append(f"duplicate dashboard uid: {uid}")
            seen_uids.add(uid)
            validate_dashboard(dashboard, errors)

    if dashboard_count != 11:
        errors.append(f"expected 11 dashboards, found {dashboard_count}")
    if errors:
        print("Monitoring dashboard validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if args.prometheus_rules_output:
        rules = prometheus_rules(dashboards)
        args.prometheus_rules_output.write_text(
            json.dumps(rules, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(
        f"Validated {dashboard_count} dashboards and their "
        "environment/grid/visualization/navigation contracts."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
