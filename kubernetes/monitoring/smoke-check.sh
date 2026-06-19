#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${MONITORING_NAMESPACE:-monitoring}"
APP_NAMESPACES="${CODEPLACE_NAMESPACES:-code-place-dev code-place-prod}"

ok() {
  echo "OK $*"
}

fail() {
  echo "FAIL $*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "missing required command: $1"
}

resource_exists() {
  kubectl -n "$1" get "$2" "$3" >/dev/null 2>&1
}

resource_count() {
  kubectl -n "$1" get "$2" -l "$3" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null | wc -w | tr -d ' '
}

require_service_endpoints() {
  local namespace="$1"
  local service="$2"
  local addresses
  addresses="$(kubectl -n "$namespace" get endpoints "$service" -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null || true)"
  if [ -z "$addresses" ]; then
    addresses="$(kubectl -n "$namespace" get endpointslice \
      -l "kubernetes.io/service-name=$service" \
      -o jsonpath='{.items[*].endpoints[*].addresses[*]}' 2>/dev/null || true)"
  fi
  [ -n "$addresses" ] || fail "$namespace service/$service has no ready endpoints"
  ok "$namespace service/$service endpoints"
}

require_label() {
  local namespace="$1"
  local resource="$2"
  local name="$3"
  local key="$4"
  local expected="$5"
  local actual
  actual="$(kubectl -n "$namespace" get "$resource" "$name" -o "jsonpath={.metadata.labels['${key//./\\.}']}")"
  [ "$actual" = "$expected" ] || fail "$resource/$name label $key expected=$expected actual=$actual"
  ok "$resource/$name label $key=$expected"
}

require_cmd kubectl

echo "==> checking Prometheus Operator CRDs"
for crd in \
  prometheusrules.monitoring.coreos.com \
  probes.monitoring.coreos.com \
  servicemonitors.monitoring.coreos.com \
  podmonitors.monitoring.coreos.com \
  alertmanagerconfigs.monitoring.coreos.com; do
  kubectl get crd "$crd" >/dev/null
  ok "CRD $crd"
done

echo "==> checking monitoring namespace resources"
kubectl get namespace "$NAMESPACE" >/dev/null
ok "namespace $NAMESPACE"

for resource in \
  "prometheusrule/codeplace-fast-alerts" \
  "servicemonitor/backend" \
  "servicemonitor/blackbox-exporter" \
  "servicemonitor/dcgm-exporter" \
  "servicemonitor/kubernetes-event-exporter" \
  "servicemonitor/longhorn" \
  "servicemonitor/otel-collector" \
  "servicemonitor/tempo" \
  "servicemonitor/traefik" \
  "servicemonitor/vllm" \
  "podmonitor/postgres" \
  "podmonitor/redis" \
  "alertmanagerconfig/codeplace-alert-routing" \
  "configmap/grafana-dashboard-codeplace" \
  "configmap/grafana-dashboard-codeplace-ai-inference" \
  "configmap/grafana-dashboard-codeplace-kubernetes-events" \
  "configmap/grafana-dashboard-codeplace-logs" \
  "configmap/grafana-dashboard-codeplace-monitoring-stack" \
  "configmap/grafana-dashboard-codeplace-public-endpoints" \
  "configmap/grafana-dashboard-codeplace-storage" \
  "configmap/grafana-dashboard-codeplace-traces" \
  "configmap/kubernetes-event-exporter-config" \
  "configmap/otel-collector-config" \
  "configmap/tempo-config" \
  "deployment/blackbox-exporter" \
  "deployment/kubernetes-event-exporter" \
  "deployment/otel-collector" \
  "deployment/tempo" \
  "service/blackbox-exporter" \
  "service/kubernetes-event-exporter" \
  "service/otel-collector" \
  "service/tempo" \
  "persistentvolumeclaim/tempo-data" \
  "probe/codeplace-public-dev-http" \
  "probe/codeplace-public-prod-http" \
  "probe/codeplace-grafana-http" \
  "probe/codeplace-hub-auth-dev-http" \
  "probe/codeplace-hub-auth-prod-http"; do
  kubectl -n "$NAMESPACE" get "$resource" >/dev/null
  ok "$resource"
done

require_label "$NAMESPACE" prometheusrule codeplace-fast-alerts release kube-prometheus-stack
require_label "$NAMESPACE" servicemonitor backend release kube-prometheus-stack
require_label "$NAMESPACE" servicemonitor traefik release kube-prometheus-stack
require_label "$NAMESPACE" podmonitor postgres release kube-prometheus-stack
require_label "$NAMESPACE" podmonitor redis release kube-prometheus-stack
require_label "$NAMESPACE" alertmanagerconfig codeplace-alert-routing alertmanagerConfig codeplace
require_label "$NAMESPACE" configmap grafana-dashboard-codeplace grafana_dashboard 1
require_label "$NAMESPACE" configmap grafana-dashboard-codeplace-ai-inference grafana_dashboard 1
require_label "$NAMESPACE" configmap grafana-dashboard-codeplace-kubernetes-events grafana_dashboard 1
require_label "$NAMESPACE" configmap grafana-dashboard-codeplace-logs grafana_dashboard 1
require_label "$NAMESPACE" configmap grafana-dashboard-codeplace-monitoring-stack grafana_dashboard 1
require_label "$NAMESPACE" configmap grafana-dashboard-codeplace-public-endpoints grafana_dashboard 1
require_label "$NAMESPACE" configmap grafana-dashboard-codeplace-storage grafana_dashboard 1
require_label "$NAMESPACE" configmap grafana-dashboard-codeplace-traces grafana_dashboard 1

if resource_exists "$NAMESPACE" secret alertmanager-contact-points; then
  kubectl -n "$NAMESPACE" get secret alertmanager-contact-points \
    -o jsonpath='{.data.webhook-url}' | grep -q . \
    || fail "secret/alertmanager-contact-points missing webhook-url key"
  ok "secret/alertmanager-contact-points webhook-url"
else
  fail "secret/alertmanager-contact-points is missing"
fi

echo "==> checking kube-prometheus-stack pods"
for selector in \
  "app.kubernetes.io/name=grafana" \
  "app.kubernetes.io/name=prometheus" \
  "app.kubernetes.io/name=alertmanager" \
  "app.kubernetes.io/name=kube-prometheus-stack-operator"; do
  kubectl -n "$NAMESPACE" wait --for=condition=Ready pod -l "$selector" --timeout=30s
  ok "pods ready for $selector"
done

echo "==> checking CodePlace monitoring pods"
for selector in \
  "app=blackbox-exporter" \
  "app.kubernetes.io/name=kubernetes-event-exporter" \
  "app=otel-collector" \
  "app=tempo"; do
  kubectl -n "$NAMESPACE" wait --for=condition=Ready pod -l "$selector" --timeout=30s
  ok "pods ready for $selector"
done

for service in \
  blackbox-exporter \
  kubernetes-event-exporter \
  otel-collector \
  tempo; do
  require_service_endpoints "$NAMESPACE" "$service"
done

if kubectl -n "$NAMESPACE" get daemonset dcgm-exporter >/dev/null 2>&1; then
  desired="$(kubectl -n "$NAMESPACE" get daemonset dcgm-exporter -o jsonpath='{.status.desiredNumberScheduled}')"
  available="$(kubectl -n "$NAMESPACE" get daemonset dcgm-exporter -o jsonpath='{.status.numberAvailable}')"
  [ "$desired" = "$available" ] || fail "daemonset/dcgm-exporter available=$available desired=$desired"
  ok "daemonset/dcgm-exporter available=$available desired=$desired"
  require_service_endpoints "$NAMESPACE" dcgm-exporter
fi

echo "==> checking optional logs stack"
if [ "$(resource_count "$NAMESPACE" pod app.kubernetes.io/name=loki)" -gt 0 ]; then
  kubectl -n "$NAMESPACE" wait --for=condition=Ready pod -l app.kubernetes.io/name=loki --timeout=30s
  ok "loki pods ready"
  if resource_exists "$NAMESPACE" service loki-gateway; then
    require_service_endpoints "$NAMESPACE" loki-gateway
  fi
else
  echo "SKIP loki pods: app.kubernetes.io/name=loki not found"
fi

if kubectl -n "$NAMESPACE" get daemonset alloy >/dev/null 2>&1; then
  desired="$(kubectl -n "$NAMESPACE" get daemonset alloy -o jsonpath='{.status.desiredNumberScheduled}')"
  available="$(kubectl -n "$NAMESPACE" get daemonset alloy -o jsonpath='{.status.numberAvailable}')"
  [ "$desired" = "$available" ] || fail "daemonset/alloy available=$available desired=$desired"
  ok "daemonset/alloy available=$available desired=$desired"
else
  echo "SKIP daemonset/alloy: not found"
fi

echo "==> checking application namespaces"
for app_namespace in $APP_NAMESPACES; do
  kubectl get namespace "$app_namespace" >/dev/null
  ok "namespace $app_namespace"
  kubectl -n "$app_namespace" get svc backend >/dev/null
  ok "$app_namespace service/backend"
  kubectl -n "$app_namespace" get svc backend -o jsonpath='{.spec.ports[*].name}' | grep -qw api \
    || fail "$app_namespace service/backend missing api port"
  ok "$app_namespace service/backend api port"
  kubectl -n "$app_namespace" wait --for=condition=Ready pod -l app=backend --timeout=30s
  ok "$app_namespace backend pods ready"
  require_service_endpoints "$app_namespace" backend
done

echo "observability smoke check completed"
