#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MONITORING_DIR="${ROOT_DIR}/kubernetes/monitoring"

require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "missing required command: ${cmd}" >&2
    exit 1
  fi
}

optional_cmd() {
  command -v "$1" >/dev/null 2>&1
}

require_cmd python3
require_cmd kubectl

echo "==> validating monitoring YAML and Grafana dashboard JSON"
python3 - <<'PY'
from pathlib import Path
import json
import sys

try:
    import yaml
except ImportError:
    yaml = None

root = Path("kubernetes/monitoring")
yaml_paths = [
    root / "kube-prometheus-stack-values.yaml",
    root / "prometheus-rules.yaml",
    root / "alertmanager-config.yaml",
    root / "alertmanager-config-email.example.yaml",
    root / "backend-service-monitor.yaml",
    root / "datastore-pod-monitors.yaml",
    root / "logs" / "loki-values.yaml",
    root / "logs" / "alloy-values.yaml",
    root / "grafana-dashboard-codeplace.yaml",
    root / "grafana-dashboard-ai-inference.yaml",
    root / "grafana-dashboard-kubernetes-events.yaml",
    root / "grafana-dashboard-logs.yaml",
    root / "grafana-dashboard-monitoring-stack.yaml",
    root / "grafana-dashboard-public-endpoints.yaml",
    root / "grafana-dashboard-storage.yaml",
    root / "grafana-dashboard-traces.yaml",
]

for path in yaml_paths:
    text = path.read_text()
    if yaml is None:
        if path.name.startswith("grafana-dashboard-"):
            print(f"missing Python module yaml; cannot extract dashboard JSON from {path}", file=sys.stderr)
            sys.exit(1)
        print(f"SKIP YAML parse {path}: Python module yaml not found")
        continue

    documents = list(yaml.safe_load_all(text))
    print(f"YAML OK {path}")
    if path.name.startswith("grafana-dashboard-"):
        data = documents[0]
        for key, value in data.get("data", {}).items():
            json.loads(value)
            print(f"JSON OK {path}:{key}")

if yaml is None:
    sys.exit(0)

rules = list(yaml.safe_load_all((root / "prometheus-rules.yaml").read_text()))[0]
rule_groups = {group["name"]: group for group in rules["spec"]["groups"]}
expected_intervals = {
    "codeplace.p0": "15s",
    "codeplace.p1": "30s",
}
for group_name, interval in expected_intervals.items():
    actual = rule_groups.get(group_name, {}).get("interval")
    if actual != interval:
        raise SystemExit(f"{group_name} interval must be {interval}, got {actual}")

alert_instances = {}
for group in rules["spec"]["groups"]:
    expected_priority = "P0" if group["name"].endswith(".p0") else "P1" if group["name"].endswith(".p1") else None
    for rule in group.get("rules", []):
        if rule.get("record"):
            if not rule.get("expr"):
                raise SystemExit(f"{rule['record']} is missing expr")
            continue
        alert_name = rule.get("alert")
        if not alert_name:
            raise SystemExit(f"rule in {group['name']} is missing alert name")
        if not rule.get("expr"):
            raise SystemExit(f"{alert_name} is missing expr")
        labels = rule.get("labels", {})
        annotations = rule.get("annotations", {})
        if labels.get("severity") not in {"critical", "warning"}:
            raise SystemExit(f"{alert_name} is missing valid severity")
        if labels.get("priority") not in {"P0", "P1"}:
            raise SystemExit(f"{alert_name} is missing valid priority")
        if expected_priority and labels.get("priority") != expected_priority:
            raise SystemExit(f"{alert_name} priority must match {group['name']}")
        for key in ("summary", "description"):
            if not annotations.get(key):
                raise SystemExit(f"{alert_name} is missing annotation {key}")
        alert_instances.setdefault(alert_name, []).append(labels)

for alert_name, labels_list in alert_instances.items():
    if len(labels_list) > 1 and any("namespace" not in labels for labels in labels_list):
        raise SystemExit(f"duplicate alert {alert_name} must include static namespace labels")
required_alerts = {
    "SubmissionCreateSystemFailures",
    "JudgeTaskFailures",
    "CeleryMinuteScheduledTaskStale",
    "CeleryDailyScheduledTaskStale",
    "CeleryWeeklyScheduledTaskStale",
    "AIHintAPIFailures",
    "AIHintBackendErrors",
    "AIHintBackendLatencyHigh",
}
missing_alerts = required_alerts - set(alert_instances)
if missing_alerts:
    raise SystemExit(f"missing required observability alerts: {sorted(missing_alerts)}")
print("PROMETHEUS RULE SHAPE OK")

alertmanager = list(yaml.safe_load_all((root / "alertmanager-config.yaml").read_text()))[0]
route = alertmanager["spec"]["route"]
if set(route.get("groupBy", [])) != {"alertname", "priority", "namespace"}:
    raise SystemExit("Alertmanager groupBy must be alertname, priority, namespace")
receivers = {receiver["name"]: receiver for receiver in alertmanager["spec"]["receivers"]}
for receiver_name in ("p0-discord", "p1-discord"):
    receiver = receivers.get(receiver_name)
    if not receiver:
        raise SystemExit(f"missing receiver {receiver_name}")
    configs = receiver.get("discordConfigs") or []
    if not configs:
        raise SystemExit(f"{receiver_name} must define discordConfigs")
    api_url = configs[0].get("apiURL", {})
    if api_url.get("name") != "alertmanager-contact-points" or api_url.get("key") != "webhook-url":
        raise SystemExit(f"{receiver_name} must use alertmanager-contact-points/webhook-url")
print("ALERTMANAGER SHAPE OK")

stack_values = yaml.safe_load((root / "kube-prometheus-stack-values.yaml").read_text())
prometheus_spec = stack_values.get("prometheus", {}).get("prometheusSpec", {})
for key in (
    "serviceMonitorSelectorNilUsesHelmValues",
    "podMonitorSelectorNilUsesHelmValues",
    "ruleSelectorNilUsesHelmValues",
):
    if prometheus_spec.get(key) is not False:
        raise SystemExit(f"kube-prometheus-stack prometheusSpec.{key} must be false")
alertmanager_selector = (
    stack_values.get("alertmanager", {})
    .get("alertmanagerSpec", {})
    .get("alertmanagerConfigSelector", {})
    .get("matchLabels", {})
)
if alertmanager_selector.get("alertmanagerConfig") != "codeplace":
    raise SystemExit("AlertmanagerConfig selector must match alertmanagerConfig=codeplace")
grafana_values = stack_values.get("grafana", {})
datasources = grafana_values.get("additionalDataSources") or []
if not any(ds.get("name") == "Loki" and ds.get("type") == "loki" for ds in datasources):
    raise SystemExit("Grafana values must provision Loki datasource")
dashboard_sidecar = grafana_values.get("sidecar", {}).get("dashboards", {})
if dashboard_sidecar.get("label") != "grafana_dashboard":
    raise SystemExit("Grafana dashboard sidecar must select grafana_dashboard label")
print("KUBE-PROMETHEUS-STACK VALUES SHAPE OK")

loki_values = yaml.safe_load((root / "logs" / "loki-values.yaml").read_text())
loki_config = loki_values.get("loki", {})
if loki_values.get("deploymentMode") != "Monolithic":
    raise SystemExit("Loki must stay in Monolithic mode for the on-prem baseline")
if loki_config.get("storage", {}).get("type") != "filesystem":
    raise SystemExit("Loki must use filesystem storage while cloud object storage is unavailable")
if loki_config.get("commonConfig", {}).get("replication_factor") != 1:
    raise SystemExit("Loki single-binary filesystem storage must keep replication_factor=1")
persistence = loki_values.get("singleBinary", {}).get("persistence", {})
if not persistence.get("enabled"):
    raise SystemExit("Loki singleBinary persistence must be enabled")
if persistence.get("storageClass") != "longhorn":
    raise SystemExit("Loki persistence must use Longhorn storageClass")
if persistence.get("size") != "50Gi":
    raise SystemExit("Loki PVC size must stay explicit at 50Gi")
limits = loki_config.get("limits_config", {})
if limits.get("retention_period") != "168h":
    raise SystemExit("Loki default retention must be 168h")
retention_by_selector = {
    stream.get("selector"): stream.get("period")
    for stream in limits.get("retention_stream", [])
}
if retention_by_selector.get('{namespace="code-place-dev"}') != "72h":
    raise SystemExit("Loki dev retention must be 72h")
if retention_by_selector.get('{namespace="code-place-prod"}') != "168h":
    raise SystemExit("Loki prod retention must be 168h")
if loki_values.get("minio", {}).get("enabled") is not False:
    raise SystemExit("Loki chart MinIO subchart must stay disabled")
print("LOKI ON-PREM STORAGE SHAPE OK")

backend_sm = yaml.safe_load((root / "backend-service-monitor.yaml").read_text())
if backend_sm.get("metadata", {}).get("labels", {}).get("release") != "kube-prometheus-stack":
    raise SystemExit("backend ServiceMonitor must keep release=kube-prometheus-stack label")
endpoint = (backend_sm.get("spec", {}).get("endpoints") or [{}])[0]
if endpoint.get("port") != "api" or endpoint.get("path") != "/metrics" or endpoint.get("interval") != "15s":
    raise SystemExit("backend ServiceMonitor must scrape api /metrics every 15s")
if backend_sm.get("spec", {}).get("selector", {}).get("matchLabels", {}).get("app") != "backend":
    raise SystemExit("backend ServiceMonitor must select app=backend")

pod_monitors = list(yaml.safe_load_all((root / "datastore-pod-monitors.yaml").read_text()))
for monitor in pod_monitors:
    name = monitor.get("metadata", {}).get("name")
    if monitor.get("metadata", {}).get("labels", {}).get("release") != "kube-prometheus-stack":
        raise SystemExit(f"{name} PodMonitor must keep release=kube-prometheus-stack label")
    endpoint = (monitor.get("spec", {}).get("podMetricsEndpoints") or [{}])[0]
    if endpoint.get("interval") != "30s":
        raise SystemExit(f"{name} PodMonitor must scrape every 30s")
print("SCRAPE RESOURCE SHAPE OK")

kustomization = yaml.safe_load((root / "kustomization.yaml").read_text())
if "./alertmanager-config-email.example.yaml" in kustomization.get("resources", []):
    raise SystemExit("email fallback example must not be included in default kustomization")
print("MONITORING KUSTOMIZATION SHAPE OK")

all_dashboard_paths = sorted(root.glob("grafana-dashboard-*.yaml"))
for dashboard_path in all_dashboard_paths:
    dashboard_map = yaml.safe_load(dashboard_path.read_text())
    for key, value in dashboard_map.get("data", {}).items():
        dashboard = json.loads(value)
        if not dashboard.get("uid") or not dashboard.get("title"):
            raise SystemExit(f"{dashboard_path}:{key} must define uid and title")
        if dashboard.get("refresh") != "30s":
            raise SystemExit(f"{dashboard_path}:{key} refresh must be 30s")
        panels = dashboard.get("panels") or []
        if not panels:
            raise SystemExit(f"{dashboard_path}:{key} must contain panels")
        for panel in panels:
            if not panel.get("title") or not panel.get("type") or not panel.get("gridPos"):
                raise SystemExit(f"{dashboard_path}:{key} has panel missing title/type/gridPos")
            for target in panel.get("targets", []):
                if not target.get("expr"):
                    raise SystemExit(f"{dashboard_path}:{key}:{panel.get('title')} has target missing expr")

dashboard_requirements = {
    "grafana-dashboard-codeplace.yaml": {
        "Submission / Judge Outcomes": [
            "codeplace_submission_create_outcome_total",
            "codeplace_judge_task_outcome_total",
        ],
        "Celery Task Runtime / Freshness": [
            "codeplace_celery_task_last_success_age_seconds",
        ],
    },
    "grafana-dashboard-ai-inference.yaml": {
        "AI Hint API Outcomes": ["codeplace_ai_hint_api_outcome_total"],
        "Backend AI Hint Streams": ["codeplace_ai_hint_requests_total"],
        "Backend AI Hint Duration": ["codeplace_ai_hint_duration_seconds_bucket"],
    },
}
dashboard_by_name = {path.name: yaml.safe_load(path.read_text()) for path in all_dashboard_paths}
for dashboard_name, panel_requirements in dashboard_requirements.items():
    dashboard_map = dashboard_by_name.get(dashboard_name)
    if not dashboard_map:
        raise SystemExit(f"missing dashboard {dashboard_name}")
    dashboards = [json.loads(value) for value in dashboard_map.get("data", {}).values()]
    panels = {
        panel.get("title"): panel
        for dashboard in dashboards
        for panel in dashboard.get("panels", [])
    }
    for title, required_expr_parts in panel_requirements.items():
        panel = panels.get(title)
        if not panel:
            raise SystemExit(f"{dashboard_name} missing panel {title}")
        exprs = "\n".join(target.get("expr", "") for target in panel.get("targets", []))
        for expr_part in required_expr_parts:
            if expr_part not in exprs:
                raise SystemExit(f"{dashboard_name}:{title} missing expr containing {expr_part}")
print("GRAFANA DASHBOARD SHAPE OK")
PY

echo "==> rendering kustomize monitoring manifests"
kubectl kustomize "${MONITORING_DIR}" >/tmp/codeplace-monitoring-render.yaml
echo "KUSTOMIZE OK kubernetes/monitoring"

echo "==> rendering application overlays for observability wiring"
for overlay in dev prod; do
  kubectl kustomize "${ROOT_DIR}/kubernetes/overlays/${overlay}" >"/tmp/codeplace-${overlay}-render.yaml"
  echo "KUSTOMIZE OK kubernetes/overlays/${overlay}"
done

python3 - <<'PY'
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    print("missing Python module yaml; cannot validate rendered application overlays", file=sys.stderr)
    sys.exit(1)


def docs_for(path):
    return [
        doc for doc in yaml.safe_load_all(Path(path).read_text())
        if isinstance(doc, dict) and doc.get("kind")
    ]


def find_one(docs, kind, name, source):
    matches = [
        doc for doc in docs
        if doc.get("kind") == kind and doc.get("metadata", {}).get("name") == name
    ]
    if len(matches) != 1:
        raise SystemExit(f"{source} expected one {kind}/{name}, got {len(matches)}")
    return matches[0]


def env_map(deployment, container_name):
    containers = deployment["spec"]["template"]["spec"].get("containers", [])
    for container in containers:
        if container.get("name") == container_name:
            return {
                env.get("name"): env.get("value")
                for env in container.get("env", [])
                if env.get("name")
            }
    raise SystemExit(f"{deployment['metadata']['name']} missing container {container_name}")


for overlay in ("dev", "prod"):
    path = f"/tmp/codeplace-{overlay}-render.yaml"
    docs = docs_for(path)
    backend_service = find_one(docs, "Service", "backend", path)
    port_names = {port.get("name") for port in backend_service.get("spec", {}).get("ports", [])}
    if "api" not in port_names:
        raise SystemExit(f"{overlay} backend Service must expose port name api for ServiceMonitor")

    for deployment_name, container_name in (
        ("backend", "backend"),
        ("celery-worker", "celery-worker"),
        ("celery-beat", "celery-beat"),
    ):
        deployment = find_one(docs, "Deployment", deployment_name, path)
        env = env_map(deployment, container_name)
        if env.get("JSON_LOGGING") != "1":
            raise SystemExit(f"{overlay} {deployment_name} must keep JSON_LOGGING=1")
        if env.get("OTEL_ENABLED") is None:
            raise SystemExit(f"{overlay} {deployment_name} must define OTEL_ENABLED")
        if env.get("OTEL_EXPORTER_OTLP_ENDPOINT") != "http://otel-collector.monitoring.svc.cluster.local:4317":
            raise SystemExit(f"{overlay} {deployment_name} must send OTLP to monitoring otel-collector")

print("APPLICATION OBSERVABILITY WIRING OK")
PY

if optional_cmd promtool; then
  echo "==> checking Prometheus rules with promtool"
  promtool check rules "${MONITORING_DIR}/prometheus-rules.yaml"
else
  echo "SKIP promtool check: promtool not found"
fi

if optional_cmd helm; then
  echo "==> rendering Helm charts"
  helm template kube-prometheus-stack prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --values "${MONITORING_DIR}/kube-prometheus-stack-values.yaml" \
    >/tmp/codeplace-kube-prometheus-stack-render.yaml
  echo "HELM OK kube-prometheus-stack"

  helm template loki grafana-community/loki \
    --namespace monitoring \
    --values "${MONITORING_DIR}/logs/loki-values.yaml" \
    >/tmp/codeplace-loki-render.yaml
  echo "HELM OK loki"

  helm template alloy grafana/alloy \
    --namespace monitoring \
    --values "${MONITORING_DIR}/logs/alloy-values.yaml" \
    >/tmp/codeplace-alloy-render.yaml
  echo "HELM OK alloy"
else
  echo "SKIP helm template: helm not found"
fi

echo "observability validation completed"
