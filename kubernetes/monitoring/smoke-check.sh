#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${MONITORING_NAMESPACE:-monitoring}"
APP_NAMESPACES="${CODEPLACE_NAMESPACES:-code-place-dev code-place-prod}"
REQUIRE_LOGS_STACK="${REQUIRE_LOGS_STACK:-1}"

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

require_jsonpath_value() {
  local namespace="$1"
  local resource="$2"
  local name="$3"
  local jsonpath="$4"
  local expected="$5"
  local actual
  actual="$(kubectl -n "$namespace" get "$resource" "$name" -o "jsonpath=$jsonpath")"
  [ "$actual" = "$expected" ] || fail "$resource/$name $jsonpath expected=$expected actual=$actual"
  ok "$resource/$name $jsonpath=$expected"
}

require_configmap_data_contains() {
  local namespace="$1"
  local name="$2"
  local key="$3"
  local expected="$4"
  local value
  value="$(kubectl -n "$namespace" get configmap "$name" -o "jsonpath={.data.${key//./\\.}}")"
  printf '%s' "$value" | grep -Fq "$expected" \
    || fail "configmap/$name $key missing expected content: $expected"
  ok "configmap/$name $key contains $expected"
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
  "configmap/kube-prometheus-stack-grafana-datasource" \
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
require_label "$NAMESPACE" configmap kube-prometheus-stack-grafana-datasource grafana_datasource 1
require_configmap_data_contains "$NAMESPACE" kube-prometheus-stack-grafana-datasource datasource.yaml 'name: Loki'
require_configmap_data_contains "$NAMESPACE" kube-prometheus-stack-grafana-datasource datasource.yaml 'uid: Loki'
require_configmap_data_contains "$NAMESPACE" kube-prometheus-stack-grafana-datasource datasource.yaml 'name: Tempo'
require_configmap_data_contains "$NAMESPACE" kube-prometheus-stack-grafana-datasource datasource.yaml 'uid: Tempo'
require_jsonpath_value "$NAMESPACE" alertmanager kube-prometheus-stack-alertmanager \
  '{.spec.alertmanagerConfigMatcherStrategy.type}' None

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

echo "==> checking logs stack"
if [ "$(resource_count "$NAMESPACE" pod app.kubernetes.io/name=loki)" -gt 0 ]; then
  kubectl -n "$NAMESPACE" get statefulset loki >/dev/null
  ok "statefulset/loki"
  require_jsonpath_value "$NAMESPACE" statefulset loki \
    '{.spec.volumeClaimTemplates[?(@.metadata.name=="storage")].spec.storageClassName}' longhorn
  require_jsonpath_value "$NAMESPACE" statefulset loki \
    '{.spec.volumeClaimTemplates[?(@.metadata.name=="storage")].spec.resources.requests.storage}' 50Gi
  kubectl -n "$NAMESPACE" wait --for=condition=Ready pod -l app.kubernetes.io/name=loki --timeout=30s
  ok "loki pods ready"
  if resource_exists "$NAMESPACE" service loki-gateway; then
    require_service_endpoints "$NAMESPACE" loki-gateway
  else
    fail "$NAMESPACE service/loki-gateway is missing"
  fi
  kubectl -n "$NAMESPACE" get persistentvolumeclaim storage-loki-0 >/dev/null
  ok "persistentvolumeclaim/storage-loki-0"
  require_label "$NAMESPACE" servicemonitor loki release kube-prometheus-stack
elif [ "$REQUIRE_LOGS_STACK" = "1" ]; then
  fail "loki pods are missing; set REQUIRE_LOGS_STACK=0 only for pre-Loki bootstrap checks"
else
  echo "SKIP loki pods: app.kubernetes.io/name=loki not found"
fi

if kubectl -n "$NAMESPACE" get daemonset alloy >/dev/null 2>&1; then
  desired="$(kubectl -n "$NAMESPACE" get daemonset alloy -o jsonpath='{.status.desiredNumberScheduled}')"
  available="$(kubectl -n "$NAMESPACE" get daemonset alloy -o jsonpath='{.status.numberAvailable}')"
  [ "$desired" = "$available" ] || fail "daemonset/alloy available=$available desired=$desired"
  ok "daemonset/alloy available=$available desired=$desired"
  require_jsonpath_value "$NAMESPACE" daemonset alloy \
    '{.spec.template.spec.volumes[?(@.name=="varlog")].hostPath.path}' /var/log
  require_jsonpath_value "$NAMESPACE" daemonset alloy \
    '{.spec.template.spec.containers[?(@.name=="alloy")].volumeMounts[?(@.name=="varlog")].mountPath}' /var/log
  require_label "$NAMESPACE" servicemonitor alloy release kube-prometheus-stack
  require_configmap_data_contains "$NAMESPACE" alloy config.alloy 'regex = "(code-place-dev|code-place-prod|monitoring)/.*|kube-system/.*/traefik"'
elif [ "$REQUIRE_LOGS_STACK" = "1" ]; then
  fail "daemonset/alloy is missing; set REQUIRE_LOGS_STACK=0 only for pre-Alloy bootstrap checks"
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
