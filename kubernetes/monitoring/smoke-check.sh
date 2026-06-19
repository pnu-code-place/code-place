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

require_cmd kubectl

echo "==> checking Prometheus Operator CRDs"
for crd in \
  prometheusrules.monitoring.coreos.com \
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
  "podmonitor/postgres" \
  "podmonitor/redis" \
  "alertmanagerconfig/codeplace-alert-routing" \
  "configmap/grafana-dashboard-codeplace" \
  "configmap/grafana-dashboard-codeplace-logs"; do
  kubectl -n "$NAMESPACE" get "$resource" >/dev/null
  ok "$resource"
done

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

echo "==> checking optional logs stack"
if kubectl -n "$NAMESPACE" get pod -l app.kubernetes.io/name=loki >/dev/null 2>&1; then
  kubectl -n "$NAMESPACE" wait --for=condition=Ready pod -l app.kubernetes.io/name=loki --timeout=30s
  ok "loki pods ready"
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
  kubectl -n "$app_namespace" wait --for=condition=Ready pod -l app=backend --timeout=30s
  ok "$app_namespace backend pods ready"
done

echo "observability smoke check completed"
