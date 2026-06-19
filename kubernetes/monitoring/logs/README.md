# CodePlace Logs Stack

This directory contains Helm values for the Kubernetes logs stack.

- Loki: monolithic mode, filesystem storage, Longhorn PVC.
- Alloy: DaemonSet log collector for `code-place-dev`, `code-place-prod`, and `monitoring`.
- Retention: `code-place-dev` 3 days, `code-place-prod` 7 days.
- Monitoring: Loki and Alloy ServiceMonitors are enabled for kube-prometheus-stack.

This is the selected baseline while cloud object storage is unavailable. Longhorn PVC is better than local hostPath or emptyDir because it gives Kubernetes-managed persistence and operationally visible volume health without introducing a new storage service. It is still not a durable log archive and should be treated as short-retention troubleshooting storage.

## Install or Upgrade

Install or upgrade kube-prometheus-stack first so the Prometheus Operator CRDs are present and the Grafana `Loki` datasource is provisioned. Then install Loki and Alloy.

```sh
helm repo add grafana-community https://grafana-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values kubernetes/monitoring/kube-prometheus-stack-values.yaml

helm upgrade --install loki grafana-community/loki \
  --namespace monitoring \
  --values kubernetes/monitoring/logs/loki-values.yaml

helm upgrade --install alloy grafana/alloy \
  --namespace monitoring \
  --values kubernetes/monitoring/logs/alloy-values.yaml
```

## Verify

Run the repository validation first:

```sh
bash kubernetes/monitoring/validate.sh
```

If `helm` is installed and the chart repos are already added, the script also renders kube-prometheus-stack, Loki, and Alloy. Without `helm`, it still validates YAML, Grafana dashboard JSON, and kustomize output.

After applying the monitoring resources to a live cluster, run the read-only smoke check:

```sh
bash kubernetes/monitoring/smoke-check.sh
```

Use `MONITORING_NAMESPACE` and `CODEPLACE_NAMESPACES` to override the defaults:

```sh
MONITORING_NAMESPACE=monitoring CODEPLACE_NAMESPACES="code-place-dev" \
  bash kubernetes/monitoring/smoke-check.sh
```

```sh
kubectl -n monitoring get pod | grep -E 'loki|alloy|grafana'
kubectl -n monitoring get pvc | grep loki
```

Grafana should show a `Loki` datasource. Useful Explore queries:

```logql
{namespace="code-place-dev"}
{namespace="code-place-prod", app="backend"} | json
{namespace="code-place-dev", container=~"backend|celery-worker|judge-server"}
```

Grafana should also show:

- `CodePlace Overview`
- `CodePlace Logs`

## Notes

This is not a horizontally scalable Loki design. It is the selected cloud-free baseline for short retention.

Keep these invariants unless the storage design changes intentionally:

- Loki stays in `Monolithic` deployment mode.
- Loki uses filesystem storage on a Longhorn PVC.
- The PVC size is explicit at `50Gi`, and `LokiPVCAlmostFull` alerts at 85%.
- Retention stays short: dev 72h, prod 168h.
- The Loki chart's MinIO subchart stays disabled. If object storage becomes available, use a separately operated S3-compatible service and migrate Loki storage deliberately.

If production log volume grows, first reduce noisy application logs or shorten retention. Increase the Longhorn PVC only after confirming available node storage and Longhorn replica health. If logs must survive a node/PVC failure domain, move prod to an internally operated S3-compatible object store such as a separately managed MinIO cluster.
