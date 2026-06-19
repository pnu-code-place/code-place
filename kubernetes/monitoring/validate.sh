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
    root / "grafana-dashboard-logs.yaml",
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
PY

echo "==> rendering kustomize monitoring manifests"
kubectl kustomize "${MONITORING_DIR}" >/tmp/codeplace-monitoring-render.yaml
echo "KUSTOMIZE OK kubernetes/monitoring"

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
