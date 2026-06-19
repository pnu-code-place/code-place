# CodePlace Logs Stack

This directory contains Helm values for the Kubernetes logs stack.

- Loki: SingleBinary mode, filesystem storage, Longhorn PVC.
- Alloy: DaemonSet log collector for every pod in `code-place-dev`, `code-place-prod`, and `monitoring`, plus Traefik pods in `kube-system`. It mounts host `/var/log` so `/var/log/pods` is readable from the Alloy container.
- Kubernetes Event Exporter: Warning events are written to stdout as JSON and collected by Alloy from the `monitoring` namespace.
- Retention: `code-place-dev` 3 days, `code-place-prod` 7 days.
- Monitoring: Loki and Alloy ServiceMonitors are enabled for kube-prometheus-stack.

This is the selected baseline while cloud object storage is unavailable. Longhorn PVC is better than local hostPath or emptyDir because it gives Kubernetes-managed persistence and operationally visible volume health without introducing a new storage service. It is still not a durable log archive and should be treated as short-retention troubleshooting storage.

Pinned chart versions:

- `prometheus-community/kube-prometheus-stack`: `86.3.1`
- `grafana/loki`: `6.55.0`
- `grafana/alloy`: `1.10.0`

## Install or Upgrade

Install or upgrade kube-prometheus-stack first so the Prometheus Operator CRDs are present and the Grafana `Loki` datasource is provisioned. Then install Loki and Alloy.
The kube-prometheus-stack values set `alertmanager.alertmanagerSpec.alertmanagerConfigMatcherStrategy.type=None` so the `monitoring` namespace AlertmanagerConfig can route CodePlace alerts whose `namespace` labels are `code-place-dev` or `code-place-prod`.

```sh
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --version 86.3.1 \
  --values kubernetes/monitoring/kube-prometheus-stack-values.yaml

helm upgrade --install loki grafana/loki \
  --namespace monitoring \
  --version 6.55.0 \
  --values kubernetes/monitoring/logs/loki-values.yaml

helm upgrade --install alloy grafana/alloy \
  --namespace monitoring \
  --version 1.10.0 \
  --values kubernetes/monitoring/logs/alloy-values.yaml
```

## Verify

After applying the monitoring resources, check the live resources directly:

```sh
kubectl -n monitoring get pod | grep -E 'loki|alloy|grafana'
kubectl -n monitoring get pvc | grep loki
kubectl -n monitoring get servicemonitor loki alloy
```

Grafana should show a `Loki` datasource. Useful Explore queries:

```logql
{namespace="code-place-dev"}
{namespace="code-place-prod", app="backend"} | json
{namespace="code-place-dev", container=~"backend|celery-worker|judge-server"}
{namespace="kube-system", app_kubernetes_io_name="traefik"} | json | DownstreamStatus >= 400
{namespace="monitoring", app_kubernetes_io_name="kubernetes-event-exporter"}
```

Grafana should also show:

- `CodePlace Overview`
- `CodePlace Logs`

## Notes

This is not a horizontally scalable Loki design. It is the selected cloud-free baseline for short retention.

Keep these invariants unless the storage design changes intentionally:

- Loki stays in `SingleBinary` deployment mode.
- Loki is installed from `grafana/loki` chart `6.55.0`. Do not upgrade the chart without revalidating rendered workloads and values compatibility.
- Loki uses filesystem storage on a Longhorn PVC.
- In the current three-node cluster, Alloy runs on every node. Loki and Tempo remain single-writer services on Longhorn PVCs, while stateless collectors and probe exporters can be replicated across nodes.
- kube-prometheus-stack Prometheus, Alertmanager, and Grafana also use Longhorn PVCs so metric data, silences, and UI state survive pod rescheduling.
- Alloy keeps namespace-based collection for `code-place-dev`, `code-place-prod`, and `monitoring`; do not depend on `app.kubernetes.io/name` for CodePlace app logs because the application manifests primarily use `app`.
- Alloy keeps `alloy.mounts.varlog=true`; otherwise the `/var/log/pods` targets are discovered but cannot be read.
- The PVC size is explicit at `50Gi`, and `LokiPVCAlmostFull` alerts at 85%.
- Retention stays short: dev 72h, prod 168h.
- The Loki chart's MinIO subchart stays disabled. If object storage becomes available, use a separately operated S3-compatible service and migrate Loki storage deliberately.

If production log volume grows, first reduce noisy application logs or shorten retention. Increase the Longhorn PVC only after confirming available node storage and Longhorn replica health. If logs must survive a node/PVC failure domain, move prod to an internally operated S3-compatible object store such as a separately managed MinIO cluster.
