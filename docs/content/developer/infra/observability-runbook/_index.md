---
date: 2026-06-19T00:00:00+09:00
draft: false
title: "Observability Runbook"
weight: 6
---

{{< callout >}}
이 문서는 Kubernetes 운영 환경에서 CodePlace 알림을 받았을 때 원인 후보를 빠르게 좁히기 위한 1차 runbook입니다. Docker Swarm monitoring은 레거시로 유지합니다.
{{< /callout >}}

## 공통 확인

알림을 받으면 먼저 scope를 확인합니다.

```sh
kubectl get ns
kubectl -n monitoring get prometheusrule,alertmanagerconfig,servicemonitor
kubectl -n monitoring get pod | grep -E 'prometheus|alertmanager|grafana|loki|alloy|otel|tempo|blackbox|event-exporter'
kubectl -n longhorn-system get pod,svc
```

Grafana에서는 `CodePlace Overview` dashboard에서 `namespace`를 알림의 namespace로 맞춥니다.
공개 URL 장애는 `CodePlace Public Endpoints` dashboard에서 먼저 봅니다.
로그 수집이나 로그 기반 확인이 필요하면 `CodePlace Logs` dashboard를 함께 봅니다.
Pod 배포/스케줄링/이미지 pull 실패는 `CodePlace Kubernetes Events` dashboard에서 Kubernetes Warning event와 kube-state-metrics 상태를 같이 봅니다.
Prometheus, Alertmanager, Grafana 자체 이상은 `CodePlace Monitoring Stack` dashboard에서 봅니다.
PVC/volume 문제가 의심되면 `CodePlace Storage` dashboard에서 Longhorn 상태를 먼저 확인합니다.

Prometheus target 확인:

```text
Status -> Targets -> backend
Status -> Targets -> postgres
Status -> Targets -> redis
Status -> Targets -> longhorn
Status -> Targets -> vllm
Status -> Targets -> dcgm-exporter
Status -> Targets -> kubernetes-event-exporter
Status -> Targets -> codeplace-public-http-dev
Status -> Targets -> codeplace-public-http-prod
```

Alertmanager 확인:

```text
Alerts -> alertname / namespace / priority
Status -> Configuration -> p0-discord / p1-discord
```

Discord webhook은 SealedSecret으로 관리합니다. AlertmanagerConfig는 최종적으로 `monitoring` namespace의 `alertmanager-contact-points` Secret key `webhook-url`을 참조하므로, 알림이 오지 않으면 SealedSecret controller와 복호화된 Secret을 함께 확인합니다.

```sh
kubectl get crd sealedsecrets.bitnami.com
kubectl get pod -A | grep -i sealed
kubectl -n monitoring get sealedsecret,secret | grep alertmanager-contact-points
kubectl -n monitoring get secret alertmanager-contact-points -o jsonpath='{.data.webhook-url}' | wc -c
kubectl -n monitoring get alertmanagerconfig codeplace-alert-routing -o yaml
kubectl -n monitoring logs alertmanager-kube-prometheus-stack-alertmanager-0 -c alertmanager --tail=100
```

`kube-prometheus-stack-values.yaml`의 `alertmanager.alertmanagerSpec.alertmanagerConfigMatcherStrategy.type`은 `None`이어야 합니다. 기본 `OnNamespace` 전략이면 `monitoring` namespace의 AlertmanagerConfig가 `namespace=code-place-dev` 또는 `namespace=code-place-prod` alert를 라우팅하지 못할 수 있습니다.

Email fallback을 켠 환경에서는 `Status -> Configuration`에서 `p0-email` / `p1-email` receiver도 확인합니다.

Monitoring stack 확인:

```sh
kubectl -n monitoring get pod | grep -E 'prometheus|alertmanager|grafana|operator'
kubectl -n monitoring get configmap kube-prometheus-stack-grafana-datasource -o yaml
kubectl -n monitoring get prometheusrule codeplace-fast-alerts -o yaml
kubectl -n monitoring get alertmanagerconfig codeplace-alert-routing -o yaml
kubectl -n monitoring get alertmanager kube-prometheus-stack-alertmanager -o jsonpath='{.spec.alertmanagerConfigMatcherStrategy.type}'
```

```promql
kube_pod_status_ready{namespace="monitoring", pod=~"prometheus-kube-prometheus-stack-prometheus-.*|alertmanager-kube-prometheus-stack-alertmanager-.*|kube-prometheus-stack-grafana-.*|grafana-.*|kube-prometheus-stack-operator-.*", condition="true"}
prometheus_notifications_alertmanagers_discovered
increase(prometheus_rule_evaluation_failures_total[5m])
increase(alertmanager_notifications_failed_total[5m])
sum by (job, namespace) (up == 0)
```

Loki 로그 확인:

```logql
{namespace="<namespace>"}
{namespace="monitoring", app_kubernetes_io_name="kubernetes-event-exporter"}
{namespace="monitoring", app_kubernetes_io_name="kubernetes-event-exporter"} |~ "FailedScheduling|ImagePullBackOff|ErrImagePull|BackOff|OOMKilling|Unhealthy|FailedMount|FailedAttachVolume"
{namespace="kube-system", app_kubernetes_io_name="traefik"} | json
{namespace="<namespace>", app="frontend"} | json
{namespace="<namespace>", app="backend"} | json
{namespace="<namespace>", app="backend"} | json | logger="frontend.error"
{namespace="<namespace>", container=~"backend|hub-auth|celery-worker|judge-server|vllm"}
```

Loki/Alloy 상태 확인:

```sh
kubectl -n monitoring get pod,pvc | grep -E 'loki|alloy'
kubectl -n monitoring logs deploy/loki-gateway --tail=100
kubectl -n monitoring logs daemonset/alloy --tail=100
```

Trace 상태 확인:

```sh
kubectl -n monitoring get pod,svc,pvc | grep -E 'otel-collector|tempo'
kubectl -n monitoring logs deploy/otel-collector --tail=100
kubectl -n monitoring logs deploy/tempo --tail=100
kubectl -n code-place-dev get deploy backend celery-worker celery-beat -o yaml | grep -A1 OTEL_ENABLED
```

Grafana에서는 `CodePlace Traces` dashboard와 `Tempo` datasource Explore를 확인합니다. dev에서 먼저 `service.name=codeplace-backend`와 `service.name=codeplace-celery` trace가 조회되어야 합니다.
Tempo에서 trace를 선택한 뒤 같은 `trace_id`를 Loki에서 조회합니다.

```logql
{namespace="<namespace>", app="backend"} | json | trace_id="<trace_id>"
{namespace="<namespace>", container=~"celery-worker|celery-beat"} | json | trace_id="<trace_id>"
```

공개 URL synthetic probe 확인:

```sh
kubectl -n monitoring get pod,svc,probe | grep -E 'blackbox|codeplace-public'
kubectl -n monitoring logs deploy/blackbox-exporter --tail=100
```

```promql
probe_success{probe_type="public-http"}
probe_http_status_code{probe_type="public-http"}
probe_duration_seconds{probe_type="public-http"}
(probe_ssl_earliest_cert_expiry{probe_type="public-http"} - time()) / 86400
```

probe 대상은 frontend와 hub-auth를 모두 포함합니다. `service` label로 어느 endpoint인지 구분합니다.

Longhorn 상태 확인:

```sh
kubectl -n longhorn-system get pod,svc
kubectl -n monitoring get servicemonitor longhorn -o yaml
```

```promql
longhorn_volume_robustness
longhorn_volume_file_system_read_only
(longhorn_node_storage_usage_bytes + longhorn_node_storage_reservation_bytes) / clamp_min(longhorn_node_storage_capacity_bytes, 1)
(longhorn_disk_usage_bytes + longhorn_disk_reservation_bytes) / clamp_min(longhorn_disk_capacity_bytes, 1)
```

vLLM 상태 확인:

```sh
kubectl -n code-place-prod get pod,svc,pvc | grep vllm
kubectl -n monitoring get servicemonitor vllm -o yaml
```

```promql
up{job="vllm", namespace="code-place-prod"}
{__name__="vllm:num_requests_running", namespace="code-place-prod"}
{__name__="vllm:num_requests_waiting", namespace="code-place-prod"}
{__name__="vllm:kv_cache_usage_perc", namespace="code-place-prod"}
histogram_quantile(0.95, sum by (le) (rate({__name__="vllm:e2e_request_latency_seconds_bucket", namespace="code-place-prod"}[10m])))
```

GPU 상태 확인:

```sh
kubectl -n monitoring get ds,svc,servicemonitor dcgm-exporter
kubectl -n monitoring logs daemonset/dcgm-exporter --tail=100
kubectl -n code-place-prod get pod -l app=vllm -o wide
```

```promql
DCGM_FI_DEV_GPU_UTIL{namespace="monitoring"}
DCGM_FI_DEV_FB_USED{namespace="monitoring"} / clamp_min(DCGM_FI_DEV_FB_USED{namespace="monitoring"} + DCGM_FI_DEV_FB_FREE{namespace="monitoring"}, 1)
DCGM_FI_DEV_GPU_TEMP{namespace="monitoring"}
DCGM_FI_DEV_XID_ERRORS{namespace="monitoring"}
```

## P0

### BackendTargetDown

증상: Prometheus가 backend `/metrics`를 1분 이상 scrape하지 못합니다.

확인:

```sh
kubectl -n <namespace> get pod,svc,endpoints backend
kubectl -n <namespace> describe pod -l app=backend
kubectl -n <namespace> logs deploy/backend --tail=100
kubectl -n monitoring get servicemonitor backend -o yaml
```

판단:

- backend Pod가 없거나 not ready이면 배포/리소스 문제입니다.
- Service endpoint가 비어 있으면 label selector 또는 readiness 문제입니다.
- backend는 떠 있는데 `/metrics`만 실패하면 app 설정 또는 ServiceMonitor port/path 문제입니다.

### Api5xxSpike

증상: backend 5xx 비율이 2분 동안 5%를 넘습니다.

확인:

```promql
sum by (namespace, status_code) (rate(codeplace_http_requests_total{namespace="<namespace>"}[5m]))
histogram_quantile(0.95, sum by (le) (rate(codeplace_http_request_duration_seconds_bucket{namespace="<namespace>"}[5m])))
```

```sh
kubectl -n <namespace> logs deploy/backend --tail=200
kubectl -n <namespace> get pod -l app=backend
kubectl -n <namespace> describe pod -l app=backend
```

Grafana Explore:

```logql
{namespace="<namespace>", app="frontend"} | json | status_code >= 500
{namespace="<namespace>", app="backend"} | json | status_code >= 500
{namespace="<namespace>", app="backend"} |= "<request_id>"
```

판단:

- 5xx와 latency가 같이 오르면 backend/DB/Redis 병목 가능성이 큽니다.
- 5xx만 증가하면 최근 배포, exception, 외부 dependency를 우선 확인합니다.
- Sentry event가 있으면 `environment`, `release`, `request_id` tag를 기준으로 같은 시간대 Loki 로그와 대조합니다.
- Sentry event가 없더라도 `codeplace_frontend_error_total`과 `frontend.error` backend JSON log를 확인합니다.
- 사용자 브라우저에서 재현 중이면 `window.__CODEPLACE_LAST_REQUEST_ID__` 값을 확인해 같은 request ID로 Loki/backend JSON log를 조회합니다.
- Frontend Sentry 설정은 image build 시점에 결정됩니다. `SENTRY_DSN`, `USE_SENTRY`, `SENTRY_ENVIRONMENT`, `APP_VERSION` 변경 후에는 frontend image rebuild가 필요합니다. DSN이 빠져 있으면 Sentry는 꺼지지만 `/api/client_error` metric/log 수집은 계속 동작해야 합니다.

### Ingress5xxSpike

증상: Traefik service 기준 5xx 비율이 2분 동안 5%를 넘습니다.

확인:

```promql
codeplace:ingress_5xx_rate2m{namespace="<namespace>"}
codeplace:ingress_request_rate2m{namespace="<namespace>"}
sum by (exported_service, code) (rate(traefik_service_requests_total{exported_service=~"<namespace>-.*"}[5m]))
sum by (service, code) (rate(traefik_service_requests_total{service=~"<namespace>-.*"}[5m]))
```

```sh
kubectl -n <namespace> get ingress,svc,endpoints
kubectl -n kube-system logs deploy/traefik --tail=200
kubectl -n kube-system get helmchartconfig traefik -o yaml
```

Grafana Explore:

```logql
{namespace="kube-system", app_kubernetes_io_name="traefik"} | json | DownstreamStatus >= 500
{namespace="kube-system", app_kubernetes_io_name="traefik"} |= "<request_id>"
```

판단:

- backend 5xx도 같이 증가하면 app/backend 문제입니다.
- ingress 5xx만 증가하면 Traefik route, Service endpoint, upstream connection 문제를 의심합니다.

### PublicEndpointDown / GrafanaPublicEndpointDown / PublicEndpointTLSCritical

증상: 공개 HTTPS endpoint synthetic probe가 실패하거나 인증서 만료가 3일 이내입니다.

확인:

```promql
probe_success{probe_type="public-http"}
probe_http_status_code{probe_type="public-http"}
probe_http_duration_seconds{probe_type="public-http"}
(probe_ssl_earliest_cert_expiry{probe_type="public-http"} - time()) / 86400
```

```sh
kubectl -n monitoring get pod,svc,probe | grep -E 'blackbox|codeplace-public|hub-auth|grafana'
kubectl -n monitoring logs deploy/blackbox-exporter --tail=200
kubectl -n <namespace> get ingress,svc,endpoints frontend hub-auth
kubectl -n kube-system logs deploy/traefik --tail=200
```

판단:

- `probe_success=0`이고 ingress/backend 지표는 정상이면 DNS, TLS, Traefik public route, frontend nginx 기본 경로 문제를 먼저 봅니다.
- `service="hub-auth"` probe가 실패하면 OAuth helper Pod, Service, Ingress, GitHub OAuth secret 설정을 우선 확인합니다.
- `service="grafana"` probe가 실패하면 Grafana Pod readiness와 별개로 Grafana ingress, Traefik route, TLS resolver, public DNS를 확인합니다.
- `probe_http_status_code`가 0이면 DNS/TCP/TLS 연결 실패 가능성이 큽니다.
- 5xx이면 Traefik/frontend/backend 로그와 같은 시간대를 대조합니다.
- TLS 만료 알림은 Traefik ACME resolver와 인증서 저장소를 확인합니다.

### JudgeAllUnavailable

증상: 사용 가능한 judge-server가 0개입니다.

확인:

```promql
codeplace_judge_server_available{namespace="<namespace>"}
codeplace_judge_server_last_heartbeat_age_seconds{namespace="<namespace>"}
codeplace_waiting_queue_length{namespace="<namespace>"}
```

```sh
kubectl -n <namespace> get pod -l app=judge-server
kubectl -n <namespace> logs deploy/judge-server --tail=200
kubectl -n <namespace> logs deploy/celery-worker --tail=200
```

판단:

- judge Pod가 not ready이면 platform/deploy 문제입니다.
- Pod는 ready인데 heartbeat가 stale이면 judge-server와 backend 통신 또는 token 문제입니다.
- waiting queue가 같이 증가하면 사용자 제출 영향이 있습니다.

### JudgeHeartbeatCritical

증상: enabled judge-server heartbeat age가 180초를 넘습니다.

확인:

```promql
max by (namespace) (codeplace_judge_server_last_heartbeat_age_seconds{namespace="<namespace>"})
topk(10, codeplace_judge_server_task_number{namespace="<namespace>"})
```

```sh
kubectl -n <namespace> get pod -l app=judge-server -o wide
kubectl -n <namespace> describe pod -l app=judge-server
```

판단:

- 특정 judge만 stale이면 해당 Pod/Node 문제입니다.
- 전체 judge가 stale이면 backend DB row, heartbeat endpoint, token 설정을 확인합니다.

### PostgresUnavailable

증상: PostgreSQL Pod가 1분 이상 ready가 아닙니다.

확인:

```sh
kubectl -n <namespace> get pod -l cnpg.io/cluster=postgres
kubectl -n <namespace> describe cluster postgres
kubectl -n <namespace> describe pod -l cnpg.io/cluster=postgres
```

판단:

- Pod scheduling 실패는 node/storage 문제입니다.
- Pod restart나 readiness 실패는 CNPG 상태와 PostgreSQL 로그를 확인합니다.

### RedisUnavailable

증상: Redis 또는 Sentinel Pod가 1분 이상 ready가 아닙니다.

확인:

```sh
kubectl -n <namespace> get pod | grep redis
kubectl -n <namespace> describe redissentinel redis
kubectl -n <namespace> describe redisreplication redis-replication
kubectl -n <namespace> logs -l app=redis-sentinel --tail=100
```

판단:

- Redis replication Pod 문제면 app cache/queue 영향이 큽니다.
- Sentinel 문제면 failover와 master discovery 영향이 큽니다.

### PostgresExporterDown / RedisExporterDown

증상: DB/Redis Pod 자체가 ready여도 exporter metric scrape가 실패합니다.

확인:

```sh
kubectl -n monitoring get podmonitor postgres redis -o yaml
kubectl -n <namespace> get pod -l cnpg.io/cluster=postgres
kubectl -n <namespace> get pod | grep redis
```

```promql
cnpg_collector_up{namespace="<namespace>", cluster="postgres"}
redis_up{namespace="<namespace>"}
```

판단:

- PostgreSQL readiness는 정상인데 `cnpg_collector_up`이 0이면 CNPG instance exporter 또는 metrics query 문제입니다.
- Redis Pod는 정상인데 `redis_up`이 0이면 exporter sidecar, Redis auth, Redis process 응답 문제입니다.
- PodMonitor target 자체가 없으면 Prometheus Operator selector 또는 Pod label/port 설정을 확인합니다.

### LokiUnavailable

증상: Loki single-binary Pod가 1분 이상 ready가 아닙니다.

확인:

```sh
kubectl -n monitoring get pod,pvc | grep loki
kubectl -n monitoring describe pod loki-0
kubectl -n monitoring logs loki-0 --tail=200
kubectl -n monitoring describe pvc -l app.kubernetes.io/name=loki
```

판단:

- PVC attach/mount 실패면 Longhorn volume 상태를 먼저 봅니다.
- readiness만 실패하면 Loki config, retention, disk full, compactor error를 확인합니다.
- Loki가 내려가도 앱 요청 처리는 계속되지만 로그 수집/조회가 끊기므로 빠르게 복구합니다.

### PrometheusUnavailable / PrometheusReplicaUnavailable / AlertmanagerUnavailable / AlertmanagerReplicaUnavailable

증상: Prometheus 또는 Alertmanager Pod가 ready가 아니거나, Prometheus ready replica가 2개 미만입니다.

확인:

```sh
kubectl -n monitoring get pod,svc | grep -E 'prometheus|alertmanager'
kubectl -n monitoring describe pod prometheus-kube-prometheus-stack-prometheus-0
kubectl -n monitoring describe pod prometheus-kube-prometheus-stack-prometheus-1
kubectl -n monitoring describe pod alertmanager-kube-prometheus-stack-alertmanager-0
kubectl -n monitoring logs prometheus-kube-prometheus-stack-prometheus-0 -c prometheus --tail=200
kubectl -n monitoring logs alertmanager-kube-prometheus-stack-alertmanager-0 -c alertmanager --tail=200
```

```promql
kube_pod_status_ready{namespace="monitoring", pod=~"prometheus-kube-prometheus-stack-prometheus-.*|alertmanager-kube-prometheus-stack-alertmanager-.*", condition="true"}
sum(kube_pod_status_ready{namespace="monitoring", condition="true", pod=~"alertmanager-kube-prometheus-stack-alertmanager-.*"})
prometheus_notifications_alertmanagers_discovered
prometheus_rule_evaluation_failures_total
```

판단:

- Prometheus ready replica가 1개만 남으면 metric 수집과 rule evaluation은 계속되지만 monitoring path HA를 잃은 상태입니다. 남은 replica까지 내려가기 전에 PVC attach, config reload, resource pressure, scheduling event를 확인합니다.
- Prometheus가 전부 down이면 metric 수집과 rule evaluation이 멈춥니다. Alertmanager가 살아 있어도 새 알림은 생성되지 않습니다.
- Alertmanager가 down이면 firing alert가 있어도 Discord/email 전달이 실패합니다. P0 수신 지연 원인으로 먼저 봅니다.
- PVC, config reload, rule syntax, resource pressure, operator reconciliation event를 함께 확인합니다.

### LonghornManagerDown / LonghornManagerReplicaUnavailable / LonghornVolumeFaulted / LonghornVolumeReadOnly

증상: Longhorn manager가 전부 ready가 아니거나, volume이 faulted/read-only 상태입니다.

확인:

```sh
kubectl -n longhorn-system get pod,svc
kubectl -n longhorn-system describe pod -l app=longhorn-manager
kubectl -n longhorn-system logs -l app=longhorn-manager --tail=200
```

```promql
sum(kube_pod_status_ready{namespace="longhorn-system", condition="true", pod=~"longhorn-manager-.*"})
kube_daemonset_status_number_available{namespace="longhorn-system", daemonset="longhorn-manager"}
kube_daemonset_status_desired_number_scheduled{namespace="longhorn-system", daemonset="longhorn-manager"}
longhorn_volume_robustness
longhorn_volume_file_system_read_only
longhorn_volume_actual_size_bytes
longhorn_volume_capacity_bytes
```

판단:

- manager가 전부 down이면 Longhorn UI/API와 metrics가 끊깁니다. node pressure, image pull, network, Longhorn system Pod 상태를 먼저 봅니다.
- volume faulted는 PVC-backed workload의 storage availability 문제입니다. affected `pvc_namespace`/`pvc`를 찾아 해당 workload 상태와 Longhorn replica 상태를 확인합니다.
- read-only volume은 쓰기 실패로 바로 이어질 수 있습니다. Loki/Tempo/PostgreSQL/Redis PVC가 대상이면 해당 관측/데이터 경로 장애로 취급합니다.

### VLLMUnavailable

증상: prod vLLM `/metrics` scrape가 2분 이상 실패합니다. AI 힌트 기능이 실패하거나 장시간 지연될 수 있습니다.

확인:

```sh
kubectl -n code-place-prod get pod,svc,endpoints,pvc | grep vllm
kubectl -n code-place-prod describe pod -l app=vllm
kubectl -n code-place-prod logs deploy/vllm --tail=200
kubectl -n monitoring get servicemonitor vllm -o yaml
```

```promql
up{job="vllm", namespace="code-place-prod"}
kube_pod_status_ready{namespace="code-place-prod", pod=~"vllm-.*", condition="true"}
```

판단:

- Pod가 pending이면 GPU node label, `runtimeClassName: nvidia`, GPU resource, Longhorn HF cache PVC attach 상태를 봅니다.
- Pod는 ready인데 scrape만 실패하면 Service port/path, vLLM `/metrics`, NetworkPolicy 여부를 확인합니다.
- backend AI hint API error가 같이 증가하면 사용자 영향이 있습니다.

### GPUXIDError

증상: NVIDIA DCGM이 GPU XID error를 1분 이상 보고합니다. vLLM이 ready여도 GPU driver, ECC, PCIe, memory, thermal 문제로 추론 장애가 날 수 있습니다.

확인:

```sh
kubectl -n monitoring logs daemonset/dcgm-exporter --tail=200
kubectl -n code-place-prod get pod -l app=vllm -o wide
kubectl -n code-place-prod logs deploy/vllm --tail=200
kubectl describe node -l workload.code-place.ai/vllm=true
```

```promql
DCGM_FI_DEV_XID_ERRORS{namespace="monitoring"}
DCGM_FI_DEV_GPU_TEMP{namespace="monitoring"}
DCGM_FI_DEV_GPU_UTIL{namespace="monitoring"}
```

판단:

- XID가 증가하고 vLLM latency/5xx가 같이 증가하면 AI hint 사용자 영향으로 봅니다.
- 같은 node에서 temperature나 utilization도 높으면 cooling, sustained load, `max-num-seqs`, KV cache 설정을 함께 낮춰 봅니다.
- XID가 반복되면 Pod 재시작만으로 닫지 말고 node driver/runtime 상태와 GPU hardware 상태를 확인합니다.

## P1

### OTelCollectorUnavailable / OTelCollectorReplicaUnavailable / OTelCollectorRefusedSpans / OTelCollectorExportFailures / TempoUnavailable / TempoPVCAlmostFull

확인:

```sh
kubectl -n monitoring get pod,svc,pvc | grep -E 'otel-collector|tempo'
kubectl -n monitoring describe pod -l app=otel-collector
kubectl -n monitoring describe pod -l app=tempo
kubectl -n monitoring logs deploy/otel-collector --tail=200
kubectl -n monitoring logs deploy/tempo --tail=200
kubectl -n monitoring describe pvc tempo-data
```

PromQL:

```promql
kube_pod_status_ready{namespace="monitoring", pod=~"otel-collector-.*|tempo-.*", condition="true"}
kube_deployment_status_replicas_available{namespace="monitoring", deployment="otel-collector"}
kube_deployment_spec_replicas{namespace="monitoring", deployment="otel-collector"}
max(kubelet_volume_stats_used_bytes{namespace="monitoring", persistentvolumeclaim="tempo-data"}) /
max(kubelet_volume_stats_capacity_bytes{namespace="monitoring", persistentvolumeclaim="tempo-data"})
sum(rate(otelcol_receiver_accepted_spans_total{namespace="monitoring"}[5m]))
sum(rate(otelcol_receiver_refused_spans_total{namespace="monitoring"}[5m]))
sum(rate(otelcol_exporter_send_failed_spans_total{namespace="monitoring"}[5m]))
```

판단:

- Collector가 down이면 dev backend/celery trace export가 실패합니다. 앱 요청 처리는 계속되지만 trace 관측이 끊깁니다.
- refused span이 증가하면 Collector receiver limit, malformed OTLP payload, backend/celery exporter 설정, collector 로그를 먼저 봅니다.
- export failure가 증가하면 Tempo readiness, `tempo.monitoring.svc.cluster.local:4317` 경로, Collector exporter queue/retry 로그를 봅니다.
- Tempo가 down이면 Collector가 span export 실패를 기록합니다.
- Tempo PVC가 85%를 넘으면 retention 단축, noisy trace sampling 조정, PVC 증설 중 하나를 먼저 결정합니다.
- 채점 병목은 Tempo에서 `judge_task`, `submission.judge`, `judge_server.select`, `judge_server.request`, `submission.result_save` span duration을 순서대로 봅니다. 선택 span이 길면 DB row lock/available judge 부족, request span이 길면 judge-server 실행/네트워크, result save span이 길면 DB lock/write 병목을 의심합니다.
- prod는 기본 `OTEL_ENABLED=0`입니다. prod trace가 없다고 해서 장애는 아니며, dev에서 Collector/Tempo를 먼저 확인한 뒤 prod 승격 여부를 결정합니다.

### ApiLatencyHigh

확인:

```promql
histogram_quantile(0.95, sum by (le) (rate(codeplace_http_request_duration_seconds_bucket{namespace="<namespace>"}[5m])))
sum by (namespace) (codeplace_waiting_queue_length{namespace="<namespace>"})
```

backend latency와 DB/Redis readiness, CPU/memory를 같이 봅니다.

### PublicEndpointDown / PublicEndpointLatencyHigh / PublicEndpointTLSExpiringSoon / BlackboxExporterUnavailable / BlackboxExporterReplicaUnavailable

확인:

```promql
probe_success{probe_type="public-http"}
probe_duration_seconds{probe_type="public-http"}
probe_http_duration_seconds{probe_type="public-http"}
(probe_ssl_earliest_cert_expiry{probe_type="public-http"} - time()) / 86400
kube_pod_status_ready{namespace="monitoring", pod=~"blackbox-exporter-.*", condition="true"}
kube_deployment_status_replicas_available{namespace="monitoring", deployment="blackbox-exporter"}
kube_deployment_spec_replicas{namespace="monitoring", deployment="blackbox-exporter"}
```

판단:

- dev endpoint down은 배포 테스트 영향으로 P1입니다. prod endpoint down은 P0입니다.
- latency가 synthetic probe에서만 높으면 public route/TLS/frontend nginx를 먼저 보고, backend latency도 높으면 API/DB/Redis 병목을 같이 봅니다.
- `BlackboxExporterUnavailable`이면 probe 자체가 죽은 것이므로 공개 URL 상태를 판단할 수 없습니다.

### GrafanaUnavailable / GrafanaMetricsTargetDown / MonitoringServiceMetricsTargetDown / PrometheusOperatorUnavailable / PrometheusConfigReloadFailed / AlertmanagerConfigReloadFailed / PrometheusRuleEvaluationFailures / PrometheusAlertmanagerDiscoveryFailed / AlertmanagerNotificationFailures

확인:

```sh
kubectl -n monitoring get pod | grep -E 'grafana|operator|prometheus|alertmanager'
kubectl -n monitoring describe pod -l app.kubernetes.io/name=grafana
kubectl -n monitoring describe pod -l app.kubernetes.io/name=prometheus-operator
kubectl -n monitoring logs deploy/kube-prometheus-stack-operator --tail=200
kubectl -n monitoring logs alertmanager-kube-prometheus-stack-alertmanager-0 -c alertmanager --tail=200
kubectl -n monitoring get prometheusrule,servicemonitor,podmonitor,alertmanagerconfig
```

PromQL:

```promql
kube_pod_status_ready{namespace="monitoring", pod=~"kube-prometheus-stack-grafana-.*|grafana-.*|kube-prometheus-stack-operator-.*", condition="true"}
up{namespace="monitoring", service="kube-prometheus-stack-grafana"}
up{namespace="monitoring", service=~"blackbox-exporter|kubernetes-event-exporter|otel-collector|tempo|kube-prometheus-stack-grafana|loki|loki-gateway|loki-canary|alloy"}
sum by (rule_group) (increase(prometheus_rule_evaluation_failures_total[5m]))
sum(kube_pod_status_ready{namespace="monitoring", condition="true", pod=~"prometheus-kube-prometheus-stack-prometheus-.*"})
prometheus_config_last_reload_successful{namespace="monitoring"}
alertmanager_config_last_reload_successful{namespace="monitoring"}
prometheus_notifications_alertmanagers_discovered
sum by (integration) (increase(alertmanager_notifications_failed_total[5m]))
sum by (job, namespace) (up == 0)
```

판단:

- Grafana만 down이면 알림은 계속 갈 수 있지만 dashboard/Explore 기반 원인 분석이 막힙니다.
- Grafana UI는 살아 있는데 metrics target만 down이면 Grafana 내부 health와 provisioning 상태를 Prometheus에서 못 봅니다. Grafana ServiceMonitor, Service port, `/metrics` 응답, Grafana 로그를 확인합니다.
- monitoring service metrics target이 down이면 Pod readiness가 정상이어도 ServiceMonitor selector, Service port name, generated Prometheus config, network path를 확인합니다.
- Operator가 down이면 새 ServiceMonitor/PodMonitor/PrometheusRule/AlertmanagerConfig 변경이 Prometheus/Alertmanager에 반영되지 않을 수 있습니다.
- rule evaluation failure가 있으면 최근 추가한 PromQL expression과 label cardinality, metric 존재 여부를 먼저 봅니다.
- Alertmanager discovery가 0이면 AlertmanagerConfig가 맞아도 Prometheus가 알림을 보낼 대상이 없습니다. Prometheus generated config와 Alertmanager Service/endpoints를 확인합니다.
- notification failure가 있으면 webhook Secret 값, Alertmanager generated config, Discord endpoint 응답, cluster outbound network, rate limit을 확인합니다. 로컬 `curl` 성공만으로 Alertmanager Pod의 egress 성공을 보장하지 않습니다.

### FrontendRuntimeErrorsSpike

확인:

```promql
sum by (namespace, surface, error_type) (increase(codeplace_frontend_error_total{namespace="<namespace>"}[10m]))
sum by (namespace, surface, error_type) (rate(codeplace_frontend_error_total{namespace="<namespace>"}[5m]))
```

Grafana Explore:

```logql
{namespace="<namespace>", app="backend"} | json | logger="frontend.error"
{namespace="<namespace>", app="backend"} | json | logger="frontend.error" | request_id="<request_id>"
```

판단:

- API 5xx/latency는 정상인데 frontend error만 증가하면 최근 frontend image, JS bundle, browser compatibility, feature flag를 먼저 봅니다.
- `surface="admin"`만 증가하면 admin bundle 또는 관리자 화면 배포 영향으로 좁힙니다.
- `error_type="unhandled_rejection"`이 많으면 API response handling, auth/session 만료 처리, network rejection을 봅니다.
- Sentry가 켜진 환경이면 같은 `release`, `environment`, `request_id`로 Sentry event와 Loki `frontend.error` 로그를 대조합니다.

### JudgeWaitingQueueBacklog / PendingSubmissionsStuck / JudgingSubmissionsStuck

확인:

```promql
codeplace_waiting_queue_length{namespace="<namespace>"}
codeplace_submission_oldest_age_seconds{namespace="<namespace>"}
codeplace_submission_status_count{namespace="<namespace>", status=~"pending|judging"}
sum by (namespace) (codeplace_judge_server_available{namespace="<namespace>"})
```

```sh
kubectl -n <namespace> logs deploy/backend --tail=200
kubectl -n <namespace> logs deploy/celery-worker --tail=200
kubectl -n <namespace> get pod -l app=judge-server
```

판단:

- queue 증가와 judge available 감소가 같이 보이면 judge-server 문제입니다.
- pending age만 증가하면 submission 생성 이후 Celery enqueue/worker dispatch/Redis queue 경로를 봅니다.
- judging age가 증가하면 judge-server 실행, judge-server `/judge` 호출, result save path, worker 로그의 `judge.tasks.judge_task`를 봅니다.
- pending/judging count는 낮지만 oldest age만 높으면 특정 제출이 고립된 상태입니다. 사용자 영향은 제한적일 수 있으나 결과 저장/상태 전환 실패를 확인합니다.

### SubmissionCreateSystemFailures / JudgeTaskFailures

확인:

```promql
sum by (namespace, scope, status) (increase(codeplace_submission_create_outcome_total{namespace="<namespace>"}[5m]))
sum by (namespace, scope, status) (increase(codeplace_judge_task_outcome_total{namespace="<namespace>"}[5m]))
```

```sh
kubectl -n <namespace> logs deploy/backend --tail=200
kubectl -n <namespace> logs deploy/celery-worker --tail=200
```

판단:

- `db_error`는 Submission row 생성이 실패한 상태입니다. PostgreSQL readiness, connection usage, lock wait, backend exception log를 봅니다.
- `enqueue_error`는 Submission row는 생성됐지만 judge task queue 등록이 실패한 상태입니다. Redis/Celery broker, worker readiness, queue metric을 먼저 봅니다.
- judge task의 `submission_missing`, `user_missing`, `error`는 Celery worker 내부 실패입니다. worker log의 exception, Submission/User row 상태, judge-server 호출, result save path를 봅니다.
- judge task의 `user_disabled`는 비활성 사용자 제출 skip으로 보고 시스템 장애 알림 대상에서 제외합니다.
- `throttled`, `invalid_captcha`, `problem_not_found`, `language_not_allowed`, `contest_permission_denied`는 사용자 입력/권한/문제 상태로 보고 시스템 장애 알림 대상에서 제외합니다.

### CeleryWorkerRestarting / CeleryBeatDown

확인:

```sh
kubectl -n <namespace> get pod -l app=celery-worker
kubectl -n <namespace> get pod -l app=celery-beat
kubectl -n <namespace> logs deploy/celery-worker --tail=200
kubectl -n <namespace> logs deploy/celery-beat --tail=200
```

Grafana Explore:

```logql
{namespace="<namespace>", container=~"celery-worker|celery-beat"}
```

### CeleryTaskFailures / CeleryTaskRetries / CeleryTaskRuntimeHigh / CeleryMinuteScheduledTaskStale / CeleryDailyScheduledTaskStale / CeleryWeeklyScheduledTaskStale

확인:

```promql
sum by (task_name, status) (increase(codeplace_celery_task_total{namespace="<namespace>"}[10m]))
histogram_quantile(0.95, sum by (task_name, le) (rate(codeplace_celery_task_runtime_seconds_bucket{namespace="<namespace>"}[10m])))
codeplace_celery_task_last_runtime_seconds{namespace="<namespace>"}
codeplace_celery_task_last_seen_age_seconds{namespace="<namespace>"}
codeplace_celery_task_last_success_age_seconds{namespace="<namespace>"}
```

Grafana Explore:

```logql
{namespace="<namespace>", container=~"celery-worker|celery-beat"} | json | task_status=~"failure|retry"
{namespace="<namespace>", container=~"celery-worker|celery-beat"} | json | task_name="<task_name>"
{namespace="<namespace>", container=~"celery-worker|celery-beat"} | json | request_id="<request_id>"
```

판단:

- 특정 task만 실패하면 최근 코드 변경, 입력 데이터, 외부 의존성을 우선 확인합니다.
- runtime만 증가하면 DB/Redis 지연, lock, worker CPU/memory, queue backlog를 같이 봅니다.
- `judge.tasks.judge_task` 실패와 `JudgeWaitingQueueBacklog`가 같이 발생하면 judge-server availability와 Redis `waiting_queue`를 우선 확인합니다.
- scheduled task stale은 beat가 task를 발행하지 못했거나 worker가 성공 종료하지 못한 상태입니다.
  `calculate_user_score_fluctuation`은 1분 주기라 10분 stale이면 빠르게 확인하고, `calculate_user_score_basis`는 일간, `update_weekly_stats`와 `update_bonus_problem`은 주간 기준으로 봅니다.
- task metric은 worker가 Redis에 누적하고 backend `/metrics` collector가 노출합니다. worker 로그에는 `task_id`, `task_name`, `task_status`, `duration_ms`, `trace_id`가 포함됩니다.

### PodCrashLooping / CodePlacePodNotReady

확인:

```sh
kubectl -n <namespace> get pod
kubectl -n <namespace> describe pod <pod>
kubectl -n <namespace> logs <pod> --previous --tail=200
```

Grafana Explore:

```logql
{namespace="<namespace>", pod="<pod>"}
{namespace="monitoring", app_kubernetes_io_name="kubernetes-event-exporter"} |= "<pod>"
```

이미지 pull, secret mount, readiness, resource limit, node scheduling을 확인합니다.

### KubernetesEventExporterUnavailable

확인:

```sh
kubectl -n monitoring get pod,svc,servicemonitor | grep event-exporter
kubectl -n monitoring describe pod -l app.kubernetes.io/name=kubernetes-event-exporter
kubectl -n monitoring logs deploy/kubernetes-event-exporter --tail=200
```

PromQL:

```promql
kube_pod_status_ready{namespace="monitoring", pod=~"kubernetes-event-exporter-.*", condition="true"}
up{job="kubernetes-event-exporter", namespace="monitoring"}
```

판단:

- exporter가 down이면 `CodePlace Kubernetes Events` dashboard의 Warning event 로그가 비어 있을 수 있습니다.
- kube-state-metrics 기반 `ImagePullBackOff`, `CrashLoopBackOff`, `OOMKilled`, `Pending` 알림은 exporter와 별개로 계속 동작합니다.
- event exporter 로그에 throttling 또는 discarded event가 보이면 `maxEventAgeSeconds`, API server 부하, 이벤트 폭주 원인을 확인합니다.

### KubernetesPodImagePullBackOff / KubernetesPodCrashLoopBackOff / KubernetesPodOOMKilled / KubernetesPodUnschedulable

확인:

```sh
kubectl -n <namespace> get pod
kubectl -n <namespace> describe pod <pod>
kubectl -n <namespace> logs <pod> --previous --tail=200
kubectl describe node <node>
```

PromQL:

```promql
kube_pod_container_status_waiting_reason{namespace="<namespace>", reason=~"ImagePullBackOff|ErrImagePull|CrashLoopBackOff|CreateContainerConfigError|CreateContainerError"}
max_over_time(kube_pod_container_status_last_terminated_reason{namespace="<namespace>", reason="OOMKilled"}[10m])
kube_pod_status_unschedulable{namespace="<namespace>"}
kube_pod_status_phase{namespace="<namespace>", phase="Pending"}
```

Grafana Explore:

```logql
{namespace="monitoring", app_kubernetes_io_name="kubernetes-event-exporter"} |= "<pod>"
{namespace="monitoring", app_kubernetes_io_name="kubernetes-event-exporter"} |~ "FailedScheduling|ImagePullBackOff|ErrImagePull|BackOff|OOMKilling|Unhealthy|FailedMount|FailedAttachVolume"
{namespace="<namespace>", pod="<pod>"}
```

판단:

- `ImagePullBackOff`/`ErrImagePull`은 image tag, registry 접근, image pull secret, node DNS/egress를 먼저 봅니다.
- `CrashLoopBackOff`는 `--previous` 로그와 직전 Warning event를 같이 봅니다. readiness 실패만으로 재시작되는지, 프로세스가 종료되는지 구분합니다.
- `OOMKilled`는 memory limit, 최근 트래픽, 캐시/큐 증가, JVM/Python heap 설정을 확인합니다.
- `Pending`/`Unschedulable`은 node capacity, taint/toleration, nodeSelector/affinity, PVC binding, Longhorn volume attach event를 확인합니다.

### CodePlaceDeploymentUnavailable / CodePlaceDeploymentRolloutStuck

확인:

```sh
kubectl -n <namespace> get deploy,rs,pod
kubectl -n <namespace> rollout status deploy/<deployment>
kubectl -n <namespace> describe deploy <deployment>
kubectl -n <namespace> get event --sort-by=.lastTimestamp | tail -50
```

PromQL:

```promql
kube_deployment_status_replicas_unavailable{namespace="<namespace>"}
kube_deployment_status_observed_generation{namespace="<namespace>"}
kube_deployment_metadata_generation{namespace="<namespace>"}
kube_pod_container_status_waiting_reason{namespace="<namespace>"}
```

판단:

- unavailable replica가 늘면 readiness probe, image pull, crash loop, resource pressure, scheduling event를 먼저 봅니다.
- observed generation이 metadata generation을 따라가지 못하면 Deployment controller reconcile, ReplicaSet 생성 실패, admission/image pull/secret 문제를 확인합니다.
- 배포 직후 API 5xx/latency와 같이 발생하면 사용자 영향이 있는 rollout 장애로 봅니다.

### CodePlaceServiceNoReadyEndpoints / VLLMServiceNoReadyEndpoints

확인:

```sh
kubectl -n <namespace> get svc,endpoints,endpointslice
kubectl -n <namespace> describe svc <service>
kubectl -n <namespace> get pod --show-labels
kubectl -n <namespace> get event --sort-by=.lastTimestamp | tail -50
```

PromQL:

```promql
kube_endpoint_address_available{namespace="<namespace>"}
kube_endpoint_address_not_ready{namespace="<namespace>"}
kube_pod_status_ready{namespace="<namespace>", condition="true"}
kube_deployment_status_replicas_unavailable{namespace="<namespace>"}
```

판단:

- Pod는 ready인데 endpoint가 0이면 Service selector label과 Pod label 불일치를 먼저 봅니다.
- Pod readiness가 같이 0이면 rollout/readiness/image pull/crash loop 문제로 봅니다.
- ingress 5xx와 같이 발생하면 Traefik route 자체보다 Service endpoint 부재가 직접 원인일 가능성이 큽니다.
- vLLM endpoint가 0이면 AI hint path만 영향받을 수 있으므로 `CodePlace AI Inference` dashboard와 GPU node scheduling 상태를 같이 봅니다.

### CodePlaceContainerCPUHigh / CodePlaceContainerMemoryHigh

확인:

```promql
topk(10, sum by (namespace, pod, container) (rate(container_cpu_usage_seconds_total{namespace="<namespace>", container!=""}[5m])))
topk(10, container_memory_working_set_bytes{namespace="<namespace>", container!=""})
```

CPU/memory가 지속적으로 높으면 replica 조정, limit 조정, 최근 배포 변경을 확인합니다.

### PostgresCollectorError / PostgresHADegraded / PostgresReplicaUnavailable / RedisReplicaUnavailable / RedisMemoryHigh / PostgresConnectionUsageHigh / PostgresLongTransactions / PostgresLockWaits / RedisConnectedClientsHigh / RedisRejectedConnections

확인:

```promql
cnpg_collector_last_collection_error{namespace="<namespace>", cluster="postgres"}
cnpg_collector_nodes_used{namespace="<namespace>", cluster="postgres"}
sum by (namespace) (kube_pod_status_ready{namespace="<namespace>", condition="true", pod=~"postgres-[0-9]+"})
sum by (namespace) (kube_pod_status_ready{namespace="<namespace>", condition="true", pod=~"redis-.*|redis-replication-.*"})
redis_memory_used_bytes{namespace="<namespace>"}
redis_memory_max_bytes{namespace="<namespace>"}
codeplace_postgres_connections{namespace="<namespace>"}
codeplace_postgres_max_connections{namespace="<namespace>"}
codeplace_postgres_long_transactions{namespace="<namespace>"}
codeplace_postgres_lock_waits{namespace="<namespace>"}
codeplace_redis_connected_clients{namespace="<namespace>"}
codeplace_redis_max_clients{namespace="<namespace>"}
increase(codeplace_redis_rejected_connections_total{namespace="<namespace>"}[5m])
```

```sh
kubectl -n <namespace> logs deploy/backend --tail=200
kubectl -n <namespace> get pod -l cnpg.io/cluster=postgres -o wide
kubectl -n <namespace> get pod -l app=redis-replication -o wide
```

판단:

- `PostgresCollectorError`는 metrics query 실패이므로 CNPG exporter 로그와 PostgreSQL 권한/상태를 확인합니다.
- `PostgresHADegraded`는 3개 instance가 서로 다른 node에 분산되지 않은 상태입니다. node 수, taint, Longhorn volume attach 상태를 확인합니다.
- `PostgresReplicaUnavailable` / `RedisReplicaUnavailable`은 3노드 분산 상태에서 남은 replica 수와 node placement를 같이 봅니다. 일부 replica만 down이면 failover 여지는 있지만 다음 장애에 취약합니다.
- `PostgresConnectionUsageHigh`는 backend connection leak, worker 동시성 증가, DB max_connections 부족, slow query 누적으로 구분합니다. API latency와 동시에 오르면 DB 병목 후보가 강합니다.
- `PostgresLongTransactions`는 transaction 범위가 긴 view/task, idle-in-transaction, migration/admin 작업을 확인합니다.
- `PostgresLockWaits`는 쓰기 contention이나 DDL/migration lock 가능성이 큽니다. 같은 시간대 backend error와 Celery runtime 증가를 같이 봅니다.
- `RedisMemoryHigh`는 Redis `maxmemory`가 0보다 클 때만 동작합니다. `maxmemory=0`이면 Redis 자체 제한이 없으므로 container memory alert를 기준으로 보고, 제한을 둘지 별도로 결정합니다.
- `RedisConnectedClientsHigh`는 connection pool 설정, worker replica/concurrency, client leak를 확인합니다.
- `RedisRejectedConnections`는 Redis `maxclients`에 실제로 걸린 상태입니다. API/cache와 Celery queue가 동시에 영향을 받을 수 있습니다.
- Redis memory가 높으면 eviction 정책, queue/backlog, cache key 증가를 확인합니다.

### PVCAlmostFull / MonitoringPVCAlmostFull

확인:

```promql
max by (namespace, persistentvolumeclaim) (kubelet_volume_stats_used_bytes{namespace="<namespace>"}) /
max by (namespace, persistentvolumeclaim) (kubelet_volume_stats_capacity_bytes{namespace="<namespace>"})
max by (namespace, persistentvolumeclaim) (kubelet_volume_stats_used_bytes{namespace="monitoring", persistentvolumeclaim!~".*loki.*|tempo-data"}) /
max by (namespace, persistentvolumeclaim) (kubelet_volume_stats_capacity_bytes{namespace="monitoring", persistentvolumeclaim!~".*loki.*|tempo-data"})
```

```sh
kubectl -n <namespace> get pvc
kubectl -n <namespace> describe pvc <pvc>
```

### LonghornVolumeDegraded / LonghornNodeNotReady / LonghornDiskNotReady / LonghornNodeStorageHigh / LonghornDiskUsageHigh

확인:

```sh
kubectl -n longhorn-system get pod
kubectl get node
kubectl describe node <node>
```

```promql
longhorn_volume_robustness == 2
longhorn_node_status{condition="ready"}
longhorn_disk_status{condition="ready"}
(longhorn_node_storage_usage_bytes + longhorn_node_storage_reservation_bytes) / clamp_min(longhorn_node_storage_capacity_bytes, 1)
(longhorn_disk_usage_bytes + longhorn_disk_reservation_bytes) / clamp_min(longhorn_disk_capacity_bytes, 1)
```

판단:

- degraded volume은 replica rebuild 중이거나 node/disk 여유가 부족한 상태일 수 있습니다.
- node/disk not ready는 앱 Pod 장애보다 먼저 storage layer 문제로 봅니다.
- storage usage가 85%를 넘으면 Loki/Tempo retention 축소, noisy 로그/trace 감소, Longhorn disk/PVC 증설 중 하나를 결정합니다.
  클라우드 object storage가 없는 현재 조건에서는 Longhorn 여유 용량이 로그/트레이스 retention의 상한입니다.

### VLLMWaitingQueueHigh / VLLMKVCacheHigh / VLLMRequestLatencyHigh

확인:

```promql
{__name__="vllm:num_requests_running", namespace="code-place-prod"}
{__name__="vllm:num_requests_waiting", namespace="code-place-prod"}
{__name__="vllm:kv_cache_usage_perc", namespace="code-place-prod"}
histogram_quantile(0.95, sum by (le) (rate({__name__="vllm:e2e_request_latency_seconds_bucket", namespace="code-place-prod"}[10m])))
histogram_quantile(0.95, sum by (le) (rate({__name__="vllm:request_queue_time_seconds_bucket", namespace="code-place-prod"}[10m])))
histogram_quantile(0.95, sum by (le) (rate({__name__="vllm:time_to_first_token_seconds_bucket", namespace="code-place-prod"}[10m])))
```

```sh
kubectl -n code-place-prod top pod -l app=vllm
kubectl -n code-place-prod describe pod -l app=vllm
kubectl -n code-place-prod logs deploy/vllm --tail=200
kubectl -n code-place-prod describe pvc vllm-hf-cache
```

판단:

- waiting queue와 queue p95가 같이 오르면 vLLM scheduling capacity 부족입니다. GPU saturation, `max-num-seqs`, KV cache pressure를 봅니다.
- KV cache가 90%를 넘으면 max model length, 동시 요청 수, prompt 길이, GPU memory utilization을 함께 봅니다.
- e2e latency만 증가하면 prompt/generation token 증가, backend streaming read timeout, vLLM 로그의 model/engine warning을 확인합니다.
  현재 vLLM은 prod 전용입니다. dev에서 AI hint를 별도 검증하려면 dev vLLM 배포와 ServiceMonitor 확장이 먼저 필요합니다.

### AIHintAPIFailures / AIHintBackendErrors / AIHintBackendLatencyHigh

확인:

```promql
sum by (namespace, scope, status) (increase(codeplace_ai_hint_api_outcome_total{namespace="<namespace>"}[5m]))
sum by (namespace, status) (increase(codeplace_ai_hint_requests_total{namespace="<namespace>"}[5m]))
histogram_quantile(0.95, sum by (namespace, le) (rate(codeplace_ai_hint_duration_seconds_bucket{namespace="<namespace>", status="success"}[10m])))
{__name__="vllm:num_requests_waiting", namespace="code-place-prod"}
histogram_quantile(0.95, sum by (le) (rate({__name__="vllm:e2e_request_latency_seconds_bucket", namespace="code-place-prod"}[10m])))
```

```sh
kubectl -n <namespace> logs deploy/backend --tail=200
kubectl -n code-place-prod get svc,endpoints vllm
kubectl -n code-place-prod logs deploy/vllm --tail=200
```

판단:

- `request_error`는 backend에서 vLLM Service까지의 endpoint, network, timeout, HTTP error를 먼저 확인합니다.
- `stream_parse_error`는 vLLM OpenAI-compatible stream format과 backend parser 호환성을 확인합니다.
- API outcome의 `permission_denied`, `problem_limit_exceeded`, `disabled`, `problem_not_found`는 시스템 장애보다 사용자/대회 상태로 먼저 봅니다.
- API outcome의 `llm_error`, `unexpected_error`, `empty_response`는 사용자 영향이 있는 실패입니다.
- backend duration과 vLLM queue/e2e latency가 같이 높으면 vLLM/GPU 병목으로 봅니다.
- backend duration만 높으면 client stream read behavior, backend worker saturation, proxy timeout을 확인합니다.

### DCGMExporterUnavailable / GPUUtilizationHigh / GPUMemoryHigh / GPUTemperatureHigh

확인:

```sh
kubectl -n monitoring get daemonset,pod,svc,servicemonitor dcgm-exporter -o wide
kubectl -n monitoring describe daemonset dcgm-exporter
kubectl -n monitoring logs daemonset/dcgm-exporter --tail=200
kubectl get node -l workload.code-place.ai/vllm=true
```

PromQL:

```promql
kube_daemonset_status_number_available{namespace="monitoring", daemonset="dcgm-exporter"}
kube_daemonset_status_desired_number_scheduled{namespace="monitoring", daemonset="dcgm-exporter"}
DCGM_FI_DEV_GPU_UTIL{namespace="monitoring"}
DCGM_FI_DEV_FB_USED{namespace="monitoring"} / clamp_min(DCGM_FI_DEV_FB_USED{namespace="monitoring"} + DCGM_FI_DEV_FB_FREE{namespace="monitoring"}, 1)
DCGM_FI_DEV_GPU_TEMP{namespace="monitoring"}
DCGM_FI_PROF_PIPE_TENSOR_ACTIVE{namespace="monitoring"}
DCGM_FI_PROF_DRAM_ACTIVE{namespace="monitoring"}
```

판단:

- exporter가 unavailable이면 GPU 상태를 볼 수 없습니다. vLLM node label, `runtimeClassName: nvidia`, NVIDIA device plugin/runtime, pod scheduling event를 확인합니다.
- GPU utilization만 높고 memory 여유가 있으면 request concurrency와 vLLM scheduling capacity 문제일 가능성이 큽니다.
- framebuffer memory usage가 높으면 KV cache pressure, `max-num-seqs`, `max-model-len`, model load 상태를 우선 봅니다.
- temperature가 높으면 AI latency보다 node cooling/thermal throttling을 먼저 의심합니다.

### LokiPVCAlmostFull

확인:

```promql
max by (namespace, persistentvolumeclaim) (kubelet_volume_stats_used_bytes{namespace="monitoring", persistentvolumeclaim=~".*loki.*"}) /
max by (namespace, persistentvolumeclaim) (kubelet_volume_stats_capacity_bytes{namespace="monitoring", persistentvolumeclaim=~".*loki.*"})
```

```sh
kubectl -n monitoring get pvc | grep loki
kubectl -n monitoring describe pvc <loki-pvc>
```

조치:

- dev/prod retention이 실제 기대대로 적용되는지 확인합니다.
- 당장 여유가 없으면 Longhorn PVC size를 증설합니다.
- 반복되면 retention 기간을 줄이거나 prod 로그 저장 방식을 내부 S3 호환 object storage로 분리합니다.

### AlloyDaemonSetUnavailable / LokiGatewayUnavailable / LokiGatewayReplicaUnavailable / LokiIngestionStalled / LokiRequestErrors / LokiCanaryMissingEntries / AlloyLokiWriteDrops / AlloyLokiWriteRetries

확인:

```sh
kubectl -n monitoring get daemonset alloy
kubectl -n monitoring describe daemonset alloy
kubectl -n monitoring logs daemonset/alloy --tail=200
kubectl -n monitoring get pod -l app.kubernetes.io/component=gateway
kubectl -n monitoring logs deploy/loki-gateway --tail=200
kubectl -n monitoring logs loki-0 --tail=200
```

PromQL:

```promql
sum(rate(loki_distributor_lines_received_total{namespace="monitoring"}[5m]))
sum(kube_pod_status_ready{namespace="monitoring", condition="true", pod=~"loki-gateway-.*"})
sum(rate(loki_request_duration_seconds_count{namespace="monitoring", status_code=~"5.."}[5m]))
sum(increase(loki_canary_missing_entries_total{namespace="monitoring"}[5m]))
sum(increase(loki_write_dropped_entries_total{namespace="monitoring"}[5m]))
sum(increase(loki_write_batch_retries_total{namespace="monitoring"}[5m]))
```

LogQL:

```logql
sum by (namespace) (rate({namespace=~"code-place-dev|code-place-prod|monitoring|kube-system"}[5m]))
sum by (namespace, app) (rate({namespace=~"code-place-dev|code-place-prod", app=~"backend|frontend"}[5m]))
sum by (namespace, container) (rate({namespace=~"code-place-dev|code-place-prod", container=~"celery-worker|celery-beat|judge-server|hub-auth|vllm"}[5m]))
```

판단:

- Alloy가 특정 node에서만 비면 해당 node의 scheduling, taint, resource pressure를 봅니다.
- Loki gateway가 비면 Alloy write와 Grafana query가 실패할 수 있습니다.
- Loki가 ready인데 ingest rate가 0이면 Alloy discovery/relabel, node별 container log path, gateway write path를 먼저 확인합니다.
- Loki 전체 ingest rate는 정상인데 특정 namespace/app 로그만 0이면 해당 Pod stdout/stderr, container restart, Alloy relabel label, node별 Alloy target discovery를 확인합니다.
- Loki 5xx가 있으면 gateway와 `loki-0` 로그를 같이 보고, PVC full/Longhorn degraded/compactor error를 확인합니다.
- Loki canary missing entry는 write 성공 후 readback 또는 storage/query path가 깨진 상태일 수 있습니다.
- Alloy write drop/retry가 있으면 Loki gateway 응답, network, Loki backpressure, Alloy resource limit을 확인합니다.

### CodePlaceNodePressure

확인:

```sh
kubectl get node
kubectl describe node <node>
kubectl top node
kubectl top pod -A --sort-by=memory
```

node pressure는 앱 문제가 아니라 cluster resource 문제일 가능성이 큽니다.

## Test Alert

Discord webhook 자체는 curl로 확인할 수 있습니다. Alertmanager routing은 임시 `PrometheusRule`로 확인합니다.
Email fallback은 SMTP 정보가 정해진 환경에서만 켭니다. `kubernetes/monitoring/alertmanager-config-email.example.yaml`의 placeholder를 실제 `smarthost`, `from`, `to`, `authUsername`으로 바꾸고 `alertmanager-email` Secret을 만든 뒤 적용합니다.

SealedSecret으로 webhook을 새로 만들 때는 운영자가 실제 cluster 공개키로 암호화합니다.

```sh
mkdir -p kubernetes/monitoring/secrets

kubectl -n monitoring create secret generic alertmanager-contact-points \
  --from-literal=webhook-url="$ALERT_WEBHOOK_URL" \
  --dry-run=client -o yaml \
  | kubeseal --controller-namespace kube-system --format yaml \
  > kubernetes/monitoring/secrets/alertmanager-contact-points.sealedsecret.yaml

kubectl apply -f kubernetes/monitoring/secrets/alertmanager-contact-points.sealedsecret.yaml
```

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: codeplace-test-alert
  namespace: monitoring
  labels:
    release: kube-prometheus-stack
spec:
  groups:
    - name: codeplace.test
      interval: 15s
      rules:
        - alert: CodePlaceTestAlert
          expr: vector(1)
          for: 30s
          labels:
            severity: critical
            priority: P0
            namespace: code-place-dev
          annotations:
            summary: "CodePlace test alert"
            description: "Discord alert routing test"
```

테스트 후 삭제합니다.

```sh
kubectl -n monitoring delete prometheusrule codeplace-test-alert
```
