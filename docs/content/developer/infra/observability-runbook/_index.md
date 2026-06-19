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
bash kubernetes/monitoring/validate.sh
kubectl get ns
kubectl -n monitoring get prometheusrule,alertmanagerconfig,servicemonitor
kubectl -n monitoring get pod | grep -E 'prometheus|alertmanager|grafana|loki|alloy'
```

Grafana에서는 `CodePlace Overview` dashboard에서 `namespace`를 알림의 namespace로 맞춥니다.
로그 수집이나 로그 기반 확인이 필요하면 `CodePlace Logs` dashboard를 함께 봅니다.

Prometheus target 확인:

```text
Status -> Targets -> backend
Status -> Targets -> postgres
Status -> Targets -> redis
```

Alertmanager 확인:

```text
Alerts -> alertname / namespace / priority
Status -> Configuration -> p0-discord / p1-discord
```

Loki 로그 확인:

```logql
{namespace="<namespace>"}
{namespace="<namespace>", app="backend"} | json
{namespace="<namespace>", container=~"backend|celery-worker|judge-server"}
```

Loki/Alloy 상태 확인:

```sh
kubectl -n monitoring get pod,pvc | grep -E 'loki|alloy'
kubectl -n monitoring logs deploy/loki-gateway --tail=100
kubectl -n monitoring logs daemonset/alloy --tail=100
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
{namespace="<namespace>", app="backend"} | json | status_code >= 500
{namespace="<namespace>", app="backend"} |= "<request_id>"
```

판단:

- 5xx와 latency가 같이 오르면 backend/DB/Redis 병목 가능성이 큽니다.
- 5xx만 증가하면 최근 배포, exception, 외부 dependency를 우선 확인합니다.
- Sentry event가 있으면 `environment`, `release`, `request_id` tag를 기준으로 같은 시간대 Loki 로그와 대조합니다.
- 사용자 브라우저에서 재현 중이면 `window.__CODEPLACE_LAST_REQUEST_ID__` 값을 확인해 같은 request ID로 Loki/backend JSON log를 조회합니다.
- Frontend Sentry 설정은 image build 시점에 결정됩니다. `SENTRY_DSN`, `USE_SENTRY`, `SENTRY_ENVIRONMENT`, `APP_VERSION` 변경 후에는 frontend image rebuild가 필요합니다.

### Ingress5xxSpike

증상: Traefik service 기준 5xx 비율이 2분 동안 5%를 넘습니다.

확인:

```promql
sum by (exported_service, code) (rate(traefik_service_requests_total{exported_service=~"<namespace>-.*"}[5m]))
```

```sh
kubectl -n <namespace> get ingress,svc,endpoints
kubectl -n kube-system logs deploy/traefik --tail=200
```

판단:

- backend 5xx도 같이 증가하면 app/backend 문제입니다.
- ingress 5xx만 증가하면 Traefik route, Service endpoint, upstream connection 문제를 의심합니다.

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

## P1

### ApiLatencyHigh

확인:

```promql
histogram_quantile(0.95, sum by (le) (rate(codeplace_http_request_duration_seconds_bucket{namespace="<namespace>"}[5m])))
sum by (namespace) (codeplace_waiting_queue_length{namespace="<namespace>"})
```

backend latency와 DB/Redis readiness, CPU/memory를 같이 봅니다.

### JudgeWaitingQueueBacklog

확인:

```promql
codeplace_waiting_queue_length{namespace="<namespace>"}
sum by (namespace) (codeplace_judge_server_available{namespace="<namespace>"})
```

queue 증가와 judge available 감소가 같이 보이면 judge-server 문제입니다. judge는 정상인데 queue만 증가하면 celery-worker 처리량을 봅니다.

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
```

이미지 pull, secret mount, readiness, resource limit, node scheduling을 확인합니다.

### CodePlaceContainerCPUHigh / CodePlaceContainerMemoryHigh

확인:

```promql
topk(10, sum by (namespace, pod, container) (rate(container_cpu_usage_seconds_total{namespace="<namespace>", container!=""}[5m])))
topk(10, container_memory_working_set_bytes{namespace="<namespace>", container!=""})
```

CPU/memory가 지속적으로 높으면 replica 조정, limit 조정, 최근 배포 변경을 확인합니다.

### PostgresCollectorError / PostgresHADegraded / RedisMemoryHigh

확인:

```promql
cnpg_collector_last_collection_error{namespace="<namespace>", cluster="postgres"}
cnpg_collector_nodes_used{namespace="<namespace>", cluster="postgres"}
redis_memory_used_bytes{namespace="<namespace>"}
redis_memory_max_bytes{namespace="<namespace>"}
```

판단:

- `PostgresCollectorError`는 metrics query 실패이므로 CNPG exporter 로그와 PostgreSQL 권한/상태를 확인합니다.
- `PostgresHADegraded`는 3개 instance가 서로 다른 node에 분산되지 않은 상태입니다. node 수, taint, Longhorn volume attach 상태를 확인합니다.
- `RedisMemoryHigh`는 Redis `maxmemory`가 0보다 클 때만 동작합니다. `maxmemory=0`이면 Redis 자체 제한이 없으므로 container memory alert를 기준으로 보고, 제한을 둘지 별도로 결정합니다.
- Redis memory가 높으면 eviction 정책, queue/backlog, cache key 증가를 확인합니다.

### PVCAlmostFull

확인:

```promql
max by (namespace, persistentvolumeclaim) (kubelet_volume_stats_used_bytes{namespace="<namespace>"}) /
max by (namespace, persistentvolumeclaim) (kubelet_volume_stats_capacity_bytes{namespace="<namespace>"})
```

```sh
kubectl -n <namespace> get pvc
kubectl -n <namespace> describe pvc <pvc>
```

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

### AlloyDaemonSetUnavailable / LokiGatewayUnavailable

확인:

```sh
kubectl -n monitoring get daemonset alloy
kubectl -n monitoring describe daemonset alloy
kubectl -n monitoring logs daemonset/alloy --tail=200
kubectl -n monitoring get pod -l app.kubernetes.io/component=gateway
kubectl -n monitoring logs deploy/loki-gateway --tail=200
```

판단:

- Alloy가 특정 node에서만 비면 해당 node의 scheduling, taint, resource pressure를 봅니다.
- Loki gateway가 비면 Alloy write와 Grafana query가 실패할 수 있습니다.

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
