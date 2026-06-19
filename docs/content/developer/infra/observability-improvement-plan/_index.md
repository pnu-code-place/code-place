---
date: 2026-06-19T00:00:00+09:00
draft: false
title: "Observability Improvement Plan"
weight: 5
---

{{< callout >}}
CodePlace 관측성 1차 구현은 Kubernetes 운영 환경을 기준으로 합니다. Docker Swarm monitoring 구성은 레거시로 유지하며 수정하지 않습니다.
{{< /callout >}}

## 1. 관측 대상

관측 대상은 운영자가 장애 발생 후 1분 안에 알림을 받고, 5분 안에 원인 후보를 좁힐 수 있도록 다음 경로로 나눕니다.

- **User Path:** synthetic public HTTPS probe, Traefik/Ingress, frontend nginx, hub-auth OAuth helper, backend Django API.
- **Submission/Judge Path:** submission 생성, Celery `judge_task`, Redis `waiting_queue`, judge-server heartbeat, judge-server `/judge` 호출, 결과 저장.
- **AI Hint Path:** backend AI hint API, vLLM OpenAI-compatible server, NVIDIA GPU/DCGM, vLLM HF cache PVC.
- **Async Jobs:** celery-worker, celery-beat, scheduled tasks.
- **Data Stores:** PostgreSQL/CNPG, Redis Sentinel.
- **Platform/Storage:** backend/frontend/celery/judge Pod, node, PVC, Longhorn volume/node/disk.
- **Client/Error:** frontend runtime error, backend exception, request ID 기반 로그, Sentry.

## 2. 구현 내용

### Metrics

backend는 `django-prometheus` 기반 `/metrics` 엔드포인트를 제공합니다. 이 엔드포인트는 ServiceMonitor가 cluster 내부에서 scrape하며 외부 Ingress에는 연결하지 않습니다.

공개 사용자 경로는 Blackbox exporter 기반 synthetic probe로 별도 확인합니다. 이 probe는 frontend, hub-auth, Grafana 공개 URL을 30초 간격으로 호출해 DNS, Traefik TLS termination, frontend nginx, OAuth helper, monitoring UI 기본 라우팅을 함께 검증합니다.

- dev frontend: `https://k3s.code-place-dev.site/`
- prod frontend: `https://code.pusan.ac.kr/`
- dev hub-auth: `https://hub-auth-dev.code-place-dev.site/`
- prod hub-auth: `https://hub-auth.code-place-dev.site/`
- Grafana: `https://monitoring.code-place-dev.site/`

추가된 CodePlace custom metrics는 다음과 같습니다.

- `codeplace_http_requests_total{method,endpoint,status_code}`
- `codeplace_http_request_duration_seconds{method,endpoint}`
- `codeplace_submission_status_count{status}`
- `codeplace_submission_oldest_age_seconds{status}`
- `codeplace_submission_judge_duration_seconds`
- `codeplace_submission_create_outcome_total{status,scope}`
- `codeplace_judge_task_outcome_total{status,scope}`
- `codeplace_waiting_queue_length`
- `codeplace_judge_server_available{hostname}`
- `codeplace_judge_server_last_heartbeat_age_seconds{hostname}`
- `codeplace_judge_server_task_number{hostname}`
- `codeplace_celery_task_total{task_name,status}`
- `codeplace_celery_task_runtime_seconds{task_name}`
- `codeplace_celery_task_last_runtime_seconds{task_name,status}`
- `codeplace_celery_task_last_seen_age_seconds{task_name,status}`
- `codeplace_celery_task_last_success_age_seconds{task_name}`
- `codeplace_ai_hint_api_outcome_total{status,scope}`
- `codeplace_ai_hint_requests_total{status}`
- `codeplace_ai_hint_duration_seconds{status}`
- `codeplace_postgres_connections`
- `codeplace_postgres_max_connections`
- `codeplace_postgres_long_transactions`
- `codeplace_postgres_lock_waits`
- `codeplace_redis_connected_clients`
- `codeplace_redis_max_clients`
- `codeplace_redis_rejected_connections_total`
- `codeplace_frontend_error_total{surface,error_type}`

운영 대시보드와 빠른 판단에는 다음 recording rule을 사용합니다.

- `codeplace:api_request_rate5m`
- `codeplace:api_5xx_rate5m`
- `codeplace:api_5xx_ratio5m`
- `codeplace:api_p95_latency_seconds5m`
- `codeplace:public_endpoint_availability5m`
- `codeplace:judge_available_total`
- `codeplace:judge_waiting_queue_length`

이 recording rule은 원본 metric을 대체하지 않습니다. 알림과 대시보드에서 반복되는 PromQL을 줄이고, user path와 judge path의 최근 상태를 한 화면에서 빠르게 읽기 위한 요약 계층입니다.

prod AI 힌트용 vLLM은 OpenAI-compatible server의 `/metrics`를 ServiceMonitor로 scrape합니다. vLLM production metrics 기준으로 다음 항목을 봅니다.

- `vllm:num_requests_running`
- `vllm:num_requests_waiting`
- `vllm:kv_cache_usage_perc`
- `vllm:e2e_request_latency_seconds`
- `vllm:request_queue_time_seconds`
- `vllm:time_to_first_token_seconds`
- `vllm:prompt_tokens`
- `vllm:generation_tokens`

vLLM이 사용하는 GPU node에는 NVIDIA DCGM exporter를 DaemonSet으로 배포합니다. 현재는 vLLM node label인 `workload.code-place.ai/vllm=true`가 붙은 node만 대상으로 하며, Prometheus는 DCGM exporter의 `:9400/metrics`를 scrape합니다.

- `DCGM_FI_DEV_GPU_UTIL`
- `DCGM_FI_DEV_FB_USED`
- `DCGM_FI_DEV_FB_FREE`
- `DCGM_FI_DEV_GPU_TEMP`
- `DCGM_FI_DEV_XID_ERRORS`
- `DCGM_FI_PROF_PIPE_TENSOR_ACTIVE`
- `DCGM_FI_PROF_DRAM_ACTIVE`

`/metrics`와 `/api/health` 요청은 API request rate/latency metric과 request completion log에서 제외합니다.

### Logs

backend는 `X-Request-ID`를 수용하고, 없으면 request ID를 생성한 뒤 응답 header로 반환합니다. Frontend axios 요청은 `X-Request-ID`를 생성해 backend로 전달하고, backend가 반환한 request ID를 axios response/error와 Sentry request context에 보존합니다. API 요청에서 Celery task를 enqueue할 때 request ID를 Celery header로 전파하고, worker 실행 중 같은 request ID를 JSON log context에 복원합니다.

frontend runtime error는 두 경로로 수집합니다.

- Sentry가 build-time `SENTRY_DSN`으로 활성화된 경우 Sentry event로 전송합니다.
- Sentry 설정이 빠져도 Vue error, `window.error`, `unhandledrejection`은 `/api/client_error`로 sanitized report를 보내고, backend가 `frontend.error` JSON log와 `codeplace_frontend_error_total{surface,error_type}` metric을 남깁니다.

Kubernetes backend/celery 환경에서는 `JSON_LOGGING=1`을 기본으로 설정합니다. JSON 로그 필드는 다음을 기준으로 합니다.

- `timestamp`
- `level`
- `logger`
- `message`
- `request_id`
- `method`
- `path`
- `status_code`
- `duration_ms`
- `user_id`
- `remote_addr`
- `task_id`
- `submission_id`
- `task_name`
- `task_status`
- `trace_id`
- `span_id`
- `frontend_surface`
- `frontend_error_type`
- `frontend_message`
- `frontend_route`
- `frontend_release`

민감 정보는 로그에 싣지 않습니다. token, password, cookie, OAuth secret, authorization header, 제출 source code는 저장 대상이 아닙니다. OpenTelemetry가 활성화된 요청/작업 로그에는 현재 span의 `trace_id`, `span_id`를 추가해 Tempo trace와 Loki JSON log를 연결합니다.

Traefik은 JSON access log를 출력하고, `X-Request-ID`, `X-Forwarded-For` header만 keep합니다. Alloy는 `kube-system` 전체가 아니라 Traefik Pod 로그만 추가 수집합니다.

frontend nginx의 Kubernetes 설정은 access log를 `/dev/stdout`, error log를 `/dev/stderr`로 출력합니다. access log는 Loki에서 파싱 가능한 JSON 형식이며, `request_id`, `method`, `path`, `status_code`, `duration_seconds`, `remote_addr`, `user_agent`, `x_forwarded_for`를 포함합니다. nginx는 들어온 `X-Request-ID`를 유지하고, 없으면 nginx `$request_id`를 생성해 응답 header와 backend proxy header로 전달합니다.

Kubernetes Pod 로그 수집은 Grafana Alloy와 Loki로 처리합니다. 클라우드 object storage를 사용할 수 없는 현재 운영 조건에서는 Loki를 SingleBinary mode로 배포하고 Longhorn PVC 기반 filesystem storage를 사용합니다.

- Loki release: `loki`, namespace: `monitoring`.
- Alloy release: `alloy`, namespace: `monitoring`.
- Loki storage: `filesystem` on Longhorn PVC.
- Loki retention: `code-place-dev` 3일, `code-place-prod` 7일.
- 수집 대상: `code-place-dev`, `code-place-prod`, `monitoring`, `kube-system`의 Traefik Pod.
- Grafana datasource: 기존 kube-prometheus-stack Grafana에 `Loki` datasource를 추가합니다.

이 구성은 클라우드 없는 단기 retention 기준선입니다. Longhorn PVC는 hostPath/emptyDir보다 낫습니다. Kubernetes에서 lifecycle을 관리할 수 있고, PVC 사용률과 Longhorn volume health를 운영자가 볼 수 있기 때문입니다. 다만 durable log archive는 아니므로 장애 분석용 단기 저장소로만 취급합니다.

현재 유지해야 하는 로그 저장소 불변 조건은 다음과 같습니다.

- Loki deployment mode는 `SingleBinary`입니다.
- Loki storage type은 `filesystem`입니다.
- Loki PVC storageClass는 `longhorn`, size는 `50Gi`입니다.
- Loki retention은 dev 72h, prod 168h입니다.
- Grafana Loki chart의 내장 MinIO subchart는 사용하지 않습니다.

prod 로그량이 커지면 먼저 noisy log를 줄이거나 retention을 줄입니다. 그래도 부족하면 Longhorn replica 상태와 node 여유 disk를 확인한 뒤 PVC를 증설합니다. 로그 저장소 장애 도메인을 더 분리해야 하면, Loki는 내부에서 별도 운영하는 S3 호환 object storage, 예를 들어 독립 MinIO cluster, 로 이전합니다.

Longhorn 자체도 kube-prometheus-stack에서 scrape합니다. `longhorn-system` namespace의 `longhorn-manager` Service를 ServiceMonitor로 연결하고, Grafana `CodePlace Storage` dashboard에서 다음 항목을 봅니다.

- Longhorn manager ready count.
- faulted/degraded/read-only volume count.
- volume robustness와 actual/capacity size.
- Longhorn node/disk 사용률.
- Longhorn manager CPU/memory.

### Tracing

OpenTelemetry는 앱 초기화 코드에 내장되어 있고, base/prod 기본값은 `OTEL_ENABLED=0`입니다. dev overlay에서만 `OTEL_ENABLED=1`로 켜서 collector/Tempo/sampling을 먼저 확인합니다.

자동 계측 대상은 Django, requests, psycopg2, Redis, Celery입니다. 제출/채점 경로에는 manual span을 추가합니다.

- `judge_task`
- `submission.judge`
- `judge_server.select`
- `judge_server.request`
- `submission.result_save`

기본 sampling 값은 `OTEL_TRACES_SAMPLER_ARG=0.05`입니다.

현재 Kubernetes manifest에는 backend/celery의 `OTEL_EXPORTER_OTLP_ENDPOINT`가 `http://otel-collector.monitoring.svc.cluster.local:4317`로 잡혀 있습니다. monitoring namespace에는 OTel Collector와 Tempo 단일 binary를 배포합니다.

- OTel Collector release: raw Kubernetes Deployment, namespace `monitoring`.
- Tempo deployment mode: single binary, namespace `monitoring`.
- Tempo storage: filesystem on Longhorn PVC.
- Tempo PVC: `tempo-data`, 20Gi.
- Tempo retention: 72h.
- Grafana datasource: 기존 kube-prometheus-stack Grafana에 `Tempo` datasource를 추가합니다.

prod tracing은 dev에서 trace ingest, query, traces-to-logs 동작과 Collector/Tempo 리소스 사용량을 확인한 뒤 별도 overlay에서 `OTEL_ENABLED=1`로 승격합니다.

## 3. Kubernetes Monitoring

신규 monitoring 리소스는 `kubernetes/monitoring` 아래에 두고, 애플리케이션 `dev/prod` overlay에 포함하지 않습니다.

- `backend-service-monitor.yaml`: `code-place-dev`와 `code-place-prod` backend `/metrics` scrape, interval 15s.
- `traefik-service-monitor.yaml`: kube-system Traefik Prometheus metrics scrape, interval 15s. `Ingress5xxSpike`의 `traefik_service_requests_total` 원천입니다.
- `blackbox-exporter.yaml`: public endpoint synthetic probe용 Blackbox exporter.
- `public-endpoint-probes.yaml`: dev/prod frontend, hub-auth, Grafana 공개 HTTPS URL Probe, interval 30s.
- `prometheus-rules.yaml`: P0/P1 fast alert rules와 운영 요약 recording rules.
- `alertmanager-config.yaml`: P0/P1 Discord alert routing.
- `grafana-dashboard-codeplace.yaml`: CodePlace overview dashboard. `namespace` 변수로 `code-place-dev`와 `code-place-prod`를 분리해서 조회합니다.
- `grafana-dashboard-ai-inference.yaml`: prod vLLM readiness, queue/cache/latency/token throughput, HF cache PVC dashboard.
- `grafana-dashboard-kubernetes-events.yaml`: image pull, CrashLoopBackOff, OOMKilled, Pending/Unschedulable 상태와 Kubernetes Warning event log dashboard.
- `grafana-dashboard-monitoring-stack.yaml`: Prometheus, Alertmanager, Grafana, Prometheus Operator readiness와 rule/notification 상태 dashboard.
- `grafana-dashboard-public-endpoints.yaml`: 공개 URL availability, HTTP status, latency, TLS expiry dashboard.
- `kubernetes-event-exporter.yaml`: Kubernetes Warning event를 stdout JSON으로 export해서 Alloy/Loki가 수집하도록 하는 exporter, ServiceMonitor, 최소 event read RBAC.
- `kube-prometheus-stack-values.yaml`: Prometheus/Alertmanager selector, Prometheus 2 replicas, Prometheus replica external label 제거, Alertmanager 2 replicas, evaluation interval, shared Grafana ingress와 dashboard sidecar 설정.
- `logs/loki-values.yaml`: Loki SingleBinary, Longhorn PVC, dev/prod retention, Loki gateway 2 replicas 설정.
- `logs/alloy-values.yaml`: Alloy DaemonSet 기반 Kubernetes Pod log collection 설정.
- `grafana-dashboard-logs.yaml`: Loki/Alloy health, Loki PVC, Loki ingest/error/canary, Alloy write backpressure, 최근 backend error, judge/celery log 조회 dashboard.
- `otel-collector.yaml`: backend/celery OTLP trace를 받아 Tempo로 전송하는 OpenTelemetry Collector.
- `tempo.yaml`: Tempo single binary, Longhorn PVC 기반 trace 저장소.
- `grafana-dashboard-traces.yaml`: Collector/Tempo readiness, span ingest/export, Tempo PVC usage dashboard.
- `longhorn-service-monitor.yaml`: Longhorn manager `/metrics` scrape, interval 30s.
- `grafana-dashboard-storage.yaml`: Longhorn volume/node/disk 상태와 storage capacity dashboard.
- `vllm-service-monitor.yaml`: prod vLLM `/metrics` scrape, interval 30s.
- `dcgm-exporter.yaml`: vLLM GPU node용 NVIDIA DCGM exporter DaemonSet/Service/ServiceMonitor.
- `kustomization.yaml`: 기존 `monitoring` namespace의 kube-prometheus-stack/Grafana/Alertmanager에 붙일 CodePlace monitoring 리소스 묶음.

`alertmanager-contact-points` Secret은 repo에 평문으로 저장하지 않습니다. backend의 `/data/config/secret.key`와 같은 비밀값이지만, 자동으로 파일이 생기는 구조는 아닙니다. 운영자는 SealedSecrets로 `alertmanager-contact-points` Secret을 생성합니다. AlertmanagerConfig는 generic webhook이 아니라 Prometheus Operator의 native `discordConfigs`를 사용합니다.

Email fallback은 SMTP host/from/to/auth가 필요하므로 기본 kustomization에는 포함하지 않습니다. SMTP 값이 정해지면 `kubernetes/monitoring/alertmanager-config-email.example.yaml`을 실제 값으로 복사하거나 패치해서 적용합니다. Prometheus Operator의 `AlertmanagerConfig`는 receiver에 `emailConfigs`를 지원하며, SMTP password는 같은 namespace의 Secret key로 참조합니다.

## 4. 빠른 알림 정책

### P0

P0는 `group_wait=10s`, `repeat_interval=15m`로 Discord에 빠르게 전달합니다.

- `BackendTargetDown`: backend scrape 실패 또는 target series missing 1분 지속.
- `Api5xxSpike`: backend 5xx 비율 5% 초과 2분 지속.
- `Ingress5xxSpike`: Traefik 5xx 비율 5% 초과 2분 지속.
- `PublicEndpointDown`: prod 공개 HTTPS endpoint probe 실패 1분 지속. frontend와 hub-auth를 포함합니다.
- `PublicEndpointTLSCritical`: prod 공개 HTTPS 인증서 만료 3일 이내.
- `JudgeAllUnavailable`: 사용 가능한 judge-server 0개 1분 지속.
- `JudgeHeartbeatCritical`: judge heartbeat age 180초 초과.
- `PostgresUnavailable`: PostgreSQL Pod not ready 또는 readiness series missing 1분 지속.
- `RedisUnavailable`: Redis Pod not ready 또는 readiness series missing 1분 지속.
- `PostgresExporterDown`: CNPG PostgreSQL exporter metric 수집 실패 2분 지속.
- `RedisExporterDown`: Redis exporter metric 수집 실패 2분 지속.
- `LokiUnavailable`: Loki single-binary Pod not ready 1분 지속.
- `LonghornManagerDown`: Longhorn manager 전부 not ready 2분 지속.
- `LonghornVolumeFaulted`: Longhorn volume faulted 1분 지속.
- `LonghornVolumeReadOnly`: Longhorn volume filesystem read-only 1분 지속.
- `VLLMUnavailable`: prod vLLM `/metrics` scrape 실패 2분 지속.
- `GPUXIDError`: NVIDIA GPU XID error 1분 지속.
- `PrometheusUnavailable`: Prometheus Pod not ready 1분 지속.
- `AlertmanagerUnavailable`: Alertmanager Pod not ready 1분 지속.

### P1

P1은 `group_wait=30s`, `repeat_interval=1h`로 전달합니다. `code-place-dev` namespace의 P1은 외부 Discord로 보내지 않고 Alertmanager/Grafana UI에만 남깁니다. `code-place-prod`, `monitoring`, `longhorn-system` 등 운영 영향이 있는 P1은 Discord로 보냅니다.

- `ApiLatencyHigh`: p95 latency 2초 초과 5분 지속.
- `PublicEndpointDown`: dev 공개 HTTPS endpoint probe 실패 2분 지속. frontend와 hub-auth를 포함합니다.
- `PublicEndpointLatencyHigh`: 공개 HTTPS probe duration 2초 초과 5분 지속.
- `PublicEndpointTLSExpiringSoon`: 공개 HTTPS 인증서 만료 14일 이내.
- `FrontendRuntimeErrorsSpike`: browser runtime error report 10개 초과/5분, 5분 지속.
- `BlackboxExporterUnavailable`: synthetic probe exporter Pod not ready 2분 지속.
- `GrafanaPublicEndpointDown`: Grafana 공개 HTTPS endpoint probe 실패 2분 지속.
- `KubernetesEventExporterUnavailable`: Kubernetes event exporter Pod not ready 2분 지속.
- `GrafanaUnavailable`: Grafana Pod not ready 2분 지속.
- `PrometheusOperatorUnavailable`: Prometheus Operator Pod not ready 2분 지속.
- `PrometheusRuleEvaluationFailures`: Prometheus rule evaluation failure 5분 지속.
- `PrometheusConfigReloadFailed`: Prometheus generated config reload 실패 또는 reload metric 누락 2분 지속.
- `PrometheusAlertmanagerDiscoveryFailed`: Prometheus가 Alertmanager target을 0개 discovery 2분 지속.
- `PrometheusReplicaUnavailable`: Prometheus ready replica 2개 미만 5분 지속.
- `AlertmanagerReplicaUnavailable`: Alertmanager ready replica 2개 미만 5분 지속.
- `AlertmanagerConfigReloadFailed`: Alertmanager generated config reload 실패 또는 reload metric 누락 2분 지속.
- `AlertmanagerNotificationFailures`: Alertmanager notification delivery failure 2분 지속.
- `JudgeWaitingQueueBacklog`: `waiting_queue` 5 초과 3분 지속.
- `SubmissionCreateSystemFailures`: 제출 생성 API에서 DB 또는 judge enqueue 실패 발생 2분 지속.
- `JudgeTaskFailures`: `judge_task`에서 submission/user lookup 또는 dispatch 실패 발생 2분 지속.
- `PendingSubmissionsStuck`: oldest pending submission age 300초 초과 3분 지속.
- `JudgingSubmissionsStuck`: oldest judging submission age 900초 초과 5분 지속.
- `CeleryWorkerRestarting`: worker restart 3회 이상/15분.
- `CeleryBeatDown`: beat Deployment available replica 0개 또는 availability metric 누락 2분 지속.
- `CeleryTaskFailures`: task failure 발생 2분 지속.
- `CeleryTaskRetries`: task retry 3회 초과/10분, 5분 지속.
- `CeleryTaskRuntimeHigh`: task p95 runtime 120초 초과 10분 지속.
- `CeleryMinuteScheduledTaskStale`: 1분 주기 점수 변동 작업 성공 age 10분 초과.
- `CeleryDailyScheduledTaskStale`: 일간 점수 기준 작업 성공 age 26시간 초과.
- `CeleryWeeklyScheduledTaskStale`: 주간 문제 통계/보너스 문제 작업 성공 age 8일 초과.
- `PodCrashLooping`: 주요 Pod restart 증가 5분 지속.
- `CodePlacePodNotReady`: 주요 앱/DB/Redis Pod not ready 5분 지속.
- `KubernetesPodImagePullBackOff`: image pull 실패 2분 지속.
- `KubernetesPodCrashLoopBackOff`: CrashLoopBackOff 5분 지속.
- `KubernetesPodOOMKilled`: OOMKilled 종료가 최근 10분 내 발생하고 2분 지속.
- `KubernetesPodUnschedulable`: Pending 또는 Unschedulable 상태 10분 지속.
- `CodePlaceDeploymentUnavailable`: 주요 Deployment unavailable replica 5분 지속.
- `CodePlaceDeploymentRolloutStuck`: Deployment observed generation 미반영 10분 지속.
- `CodePlaceServiceNoReadyEndpoints`: 주요 Service ready endpoint 0개 또는 endpoint availability metric 누락 2분 지속.
- `VLLMServiceNoReadyEndpoints`: prod vLLM Service ready endpoint 0개 또는 endpoint availability metric 누락 2분 지속.
- `CodePlaceContainerCPUHigh`: 주요 컨테이너 CPU limit 사용률 80% 초과 10분 지속.
- `CodePlaceContainerMemoryHigh`: 주요 컨테이너 memory limit 사용률 85% 초과 10분 지속.
- `PostgresCollectorError`: CNPG PostgreSQL metrics collection error 5분 지속.
- `PostgresHADegraded`: PostgreSQL instance가 3개 node에 분산되지 않음 10분 지속.
- `RedisMemoryHigh`: Redis memory 사용률 85% 초과 10분 지속.
- `PostgresConnectionUsageHigh`: backend 기준 PostgreSQL connection/max_connections 80% 초과 10분 지속.
- `PostgresLongTransactions`: 5분 초과 transaction이 10분 지속.
- `PostgresLockWaits`: lock wait가 5분 지속.
- `RedisConnectedClientsHigh`: backend 기준 Redis connected_clients/maxclients 80% 초과 10분 지속.
- `RedisRejectedConnections`: Redis rejected connection 증가 2분 지속.
- `PVCAlmostFull`: PVC 사용률 85% 초과 10분 지속.
- `LokiPVCAlmostFull`: Loki Longhorn PVC 사용률 85% 초과 10분 지속.
- `AlloyDaemonSetUnavailable`: Alloy log collector가 모든 node에서 available하지 않음 5분 지속.
- `LokiGatewayUnavailable`: Loki gateway Pod not ready 2분 지속.
- `LokiGatewayReplicaUnavailable`: Loki gateway ready replica 2개 미만 5분 지속.
- `LokiIngestionStalled`: Loki log line 수신량 0이 10분 지속.
- `LokiRequestErrors`: Loki 5xx response 발생 5분 지속.
- `LokiCanaryMissingEntries`: Loki canary write/readback 누락 발생 5분 지속.
- `AlloyLokiWriteDrops`: Alloy가 Loki write 전 log entry drop 2분 지속.
- `AlloyLokiWriteRetries`: Alloy Loki write batch retry 5분 지속.
- `OTelCollectorUnavailable`: OpenTelemetry Collector Pod not ready 2분 지속.
- `OTelCollectorRefusedSpans`: Collector span 수신 거부 발생 2분 지속.
- `OTelCollectorExportFailures`: Collector span export 실패 발생 2분 지속.
- `TempoUnavailable`: Tempo Pod not ready 2분 지속.
- `TempoPVCAlmostFull`: Tempo PVC 사용률 85% 초과 10분.
- `LonghornVolumeDegraded`: Longhorn volume degraded 5분 지속.
- `LonghornNodeNotReady`: Longhorn node not ready 5분 지속.
- `LonghornDiskNotReady`: Longhorn disk not ready 5분 지속.
- `LonghornNodeStorageHigh`: Longhorn node storage 사용/예약률 85% 초과 10분.
- `LonghornDiskUsageHigh`: Longhorn disk 사용/예약률 85% 초과 10분.
- `VLLMWaitingQueueHigh`: prod vLLM waiting request 5 초과 5분 지속.
- `VLLMKVCacheHigh`: prod vLLM KV cache 사용률 90% 초과 10분 지속.
- `VLLMRequestLatencyHigh`: prod vLLM p95 e2e latency 60초 초과 10분 지속.
- `AIHintBackendErrors`: backend AI hint stream request/parse/internal error 발생 2분 지속.
- `AIHintBackendLatencyHigh`: backend AI hint successful stream p95 duration 120초 초과 10분 지속.
- `AIHintAPIFailures`: AI hint 사용자-facing API에서 LLM error, unexpected error, empty response 발생 2분 지속.
- `DCGMExporterUnavailable`: DCGM exporter DaemonSet unavailable 2분 지속.
- `GPUUtilizationHigh`: GPU utilization 95% 초과 15분 지속.
- `GPUMemoryHigh`: GPU framebuffer memory usage 90% 초과 10분 지속.
- `GPUTemperatureHigh`: GPU temperature 85C 초과 10분 지속.
- `CodePlaceNodePressure`: node memory/disk/PID pressure 5분 지속.

## 5. 운영 확인 절차

1. kube-prometheus-stack을 `monitoring` namespace에 설치하거나 업그레이드할 때 `kubernetes/monitoring/kube-prometheus-stack-values.yaml`을 함께 적용합니다. 이 값 파일이 Prometheus 2 replicas, Alertmanager 2 replicas, `monitoring.code-place-dev.site` Grafana ingress와 dashboard sidecar 설정까지 관리합니다. Prometheus Operator CRD가 `AlertmanagerConfig.discordConfigs`를 지원하는 버전인지 확인합니다.
   - `helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack --namespace monitoring --version 86.3.1 --values kubernetes/monitoring/kube-prometheus-stack-values.yaml`
   - values는 `alertmanager.alertmanagerSpec.alertmanagerConfigMatcherStrategy.type=None`을 설정합니다. AlertmanagerConfig는 `monitoring` namespace에 있지만 CodePlace alert의 `namespace` label은 `code-place-dev`/`code-place-prod`이므로, 기본 `OnNamespace` matcher를 쓰면 외부 namespace alert가 Discord receiver까지 도달하지 않을 수 있습니다.
2. `alertmanager-contact-points` Secret을 운영 클러스터의 `monitoring` namespace에 SealedSecret으로 생성합니다. 이 값은 Kubernetes Secret으로 참조되며, Pod 파일로 mount하지 않습니다.
   Email fallback을 켤 경우 SMTP 정보를 별도로 정한 뒤 `alertmanager-email` Secret과 email AlertmanagerConfig를 추가 적용합니다.
3. Loki와 Alloy를 설치합니다.
   - `helm upgrade --install loki grafana/loki --namespace monitoring --version 6.55.0 --values kubernetes/monitoring/logs/loki-values.yaml`
   - `helm upgrade --install alloy grafana/alloy --namespace monitoring --version 1.10.0 --values kubernetes/monitoring/logs/alloy-values.yaml`
4. 애플리케이션은 환경별 overlay로 적용합니다.
   - dev: `kubectl apply -k kubernetes/overlays/dev`
   - prod: `kubectl apply -k kubernetes/overlays/prod`
5. CodePlace monitoring 리소스는 기존 kube-prometheus-stack이 있는 클러스터에 별도로 적용합니다.
   - `kubectl apply -k kubernetes/monitoring`
6. Prometheus target에서 `backend`, `longhorn`, `vllm`, `blackbox-exporter`, `kubernetes-event-exporter`, `codeplace-public-http-dev`, `codeplace-public-http-prod`, `codeplace-grafana-http`가 healthy인지 확인합니다.
7. Grafana의 `CodePlace Public Endpoints` dashboard에서 prod/dev/Grafana availability, HTTP status, latency, TLS expiry panel이 비어 있지 않은지 확인합니다.
8. Grafana의 `CodePlace Overview` dashboard에서 recording rule 기반 request rate, 5xx ratio, p95 latency, judge availability, waiting queue와 frontend runtime error, submission status, submission/judge outcome, oldest in-flight submission age, judge heartbeat, Celery task throughput/runtime, Pod readiness/restart, CPU/memory, PVC, Deployment unavailable/rollout, Service ready endpoint, PostgreSQL/Redis readiness/connection/lock/client panel을 확인합니다.
9. Grafana의 `CodePlace Logs` dashboard에서 Loki ready, Alloy node coverage, Loki PVC usage, ingress/frontend 4xx/5xx, 최근 backend error, frontend runtime error, judge/celery log panel을 확인합니다.
10. Grafana의 `CodePlace Logs` dashboard에서 `request_id` 변수에 실제 응답 header 또는 JSON log의 request ID를 넣고 해당 요청 로그가 좁혀지는지 확인합니다.
11. Grafana의 `CodePlace Kubernetes Events` dashboard에서 event exporter ready, image pull, CrashLoopBackOff, OOMKilled, Pending/Unschedulable, Kubernetes Warning event panel을 확인합니다.
12. Grafana의 `CodePlace Monitoring Stack` dashboard에서 Prometheus, Alertmanager, Grafana, operator readiness, target scrape failure, rule evaluation failure, notification failure panel을 확인합니다.
13. Grafana의 `CodePlace Traces` dashboard에서 Tempo ready, OTel Collector ready, trace receive/export rate, Tempo PVC usage를 확인합니다.
14. Grafana의 `CodePlace Storage` dashboard에서 Longhorn manager, volume robustness, node/disk usage panel이 비어 있지 않은지 확인합니다.
15. Grafana의 `CodePlace AI Inference` dashboard에서 vLLM scrape, pod ready, waiting/running requests, KV cache, p95 latency, token throughput, HF cache PVC, AI hint API outcome, backend AI hint stream status/duration, GPU utilization/memory/temperature/XID panel이 비어 있지 않은지 확인합니다.
16. Grafana Explore에서 `Loki` datasource를 선택하고 `{namespace="code-place-dev"}` 쿼리가 로그를 반환하는지 확인합니다.
17. Grafana Explore에서 `Loki` datasource를 선택하고 `{namespace="monitoring", app_kubernetes_io_name="kubernetes-event-exporter"}` 쿼리가 Kubernetes Warning event를 반환하는지 확인합니다.
18. Grafana Explore에서 `Tempo` datasource를 선택하고 `service.name=codeplace-backend` 또는 `service.name=codeplace-celery` trace가 조회되는지 확인합니다.
19. test alert 또는 임시 rule로 P0 webhook 수신 시간이 1분 이내인지 확인합니다.

운영 적용 전제는 다음과 같습니다.

- `/metrics`는 cluster 내부 scrape 전용이며 외부 Ingress에 노출하지 않습니다.
- 공개 URL synthetic probe는 monitoring namespace 내부에서 외부 도메인으로 나가는 HTTPS 요청입니다. DNS, outbound network, TLS, Traefik/frontend/hub-auth 경로를 함께 검증하지만 브라우저 JS runtime error를 대체하지는 않습니다.
- Discord webhook URL은 Git에 평문으로 저장하지 않습니다. 운영 Secret은 SealedSecret으로 관리합니다.
- Docker Swarm monitoring 구성은 레거시로 유지하고 신규 관측성 리소스와 분리합니다.
- OpenTelemetry는 base/prod `OTEL_ENABLED=0` 기본값을 유지하고 dev overlay에서 먼저 활성화합니다.
- P0/P1 알림 라우팅은 AlertmanagerConfig로 관리하며 Grafana UI 수동 설정에 의존하지 않습니다. dev P1은 `dev-p1-muted` receiver로 보내 외부 전송을 막고, prod/monitoring P1은 Discord receiver로 보냅니다.
- Metrics backend는 kube-prometheus-stack의 Prometheus입니다. Mimir는 현재 온프렘 단기 운영 기준선에 포함하지 않습니다.
- 로그 수집은 Grafana Alloy와 Loki로 관리하며 Promtail은 신규 도입하지 않습니다.
- Kubernetes event는 Kubernetes Event Exporter가 Warning event만 stdout JSON으로 내보내고, Alloy가 일반 Pod log와 같은 경로로 Loki에 적재합니다.
- PostgreSQL은 CNPG instance exporter와 PodMonitor로 `cnpg_collector_*` 지표를 수집합니다. Redis는 Opstree Redis exporter sidecar와 PodMonitor로 `redis_*` 지표를 수집합니다.
- Sentry backend SDK는 기본 PII 자동 전송을 비활성화하고 전송 직전 `authorization`, `cookie`, `password`, `token`, `secret`, 제출 source code 계열 필드를 redaction합니다. 사용자 영향 분석은 Sentry event와 request_id 기반 backend JSON log를 함께 사용합니다.
- Frontend는 axios 요청마다 `X-Request-ID`를 전파하고 마지막 request ID를 `window.__CODEPLACE_LAST_REQUEST_ID__`와 Sentry request context 및 `/api/client_error` report에 저장합니다.
- Frontend Sentry 설정은 빌드 시점 값입니다. `APP_VERSION`, `SENTRY_ENVIRONMENT`, `SENTRY_DSN`, `USE_SENTRY`는 frontend image build-arg로 주입하며, Kubernetes Deployment의 런타임 env만 변경해도 이미 빌드된 JS bundle에는 반영되지 않습니다. DSN이 없으면 Sentry는 비활성화되지만 `/api/client_error` 기반 metric/log는 계속 동작합니다.
- Backend/Celery Sentry release는 `SENTRY_RELEASE` env가 있으면 사용합니다. 이미지 태그와 동일한 commit SHA를 넣어 Grafana/Loki/Sentry 간 배포 기준을 맞추는 것을 권장합니다.
- Tempo tracing은 monitoring namespace에 배포하지만, prod app trace export는 dev 확인 후 별도 승격합니다.
- vLLM은 prod overlay에만 포함되어 있으므로 vLLM ServiceMonitor와 AI Inference dashboard도 `code-place-prod`를 기준으로 조회합니다. dev에 vLLM을 올리면 별도 dev ServiceMonitor/Probe 또는 namespace selector 확장이 필요합니다.
- DCGM exporter는 `workload.code-place.ai/vllm=true` node label을 기준으로 배포합니다. GPU node가 늘어나거나 vLLM 외 GPU workload를 운영하면 selector와 dashboard scope를 확장해야 합니다.

## 6. 검증

로컬 검증 항목은 다음과 같습니다.

- Python compile: `python3 -m compileall backend/account backend/judge backend/oj backend/utils`
- Django check: `/tmp/code-place-backend-venv/bin/python manage.py check --settings=oj.settings`
- Metrics endpoint: Django test client 기준 `/metrics` 200 및 `codeplace_*` metric 포함 확인
- Kubernetes app render: `kubectl kustomize kubernetes/overlays/dev`, `kubectl kustomize kubernetes/overlays/prod`
- Kubernetes monitoring render: `kubectl kustomize kubernetes/monitoring`
- Logs values YAML parse: `kubernetes/monitoring/logs/loki-values.yaml`, `kubernetes/monitoring/logs/alloy-values.yaml`
- Grafana dashboard JSON parse: `grafana-dashboard-codeplace.yaml`, `grafana-dashboard-logs.yaml`
- Prometheus rule syntax: `promtool check rules`에 `PrometheusRule.spec.groups`를 추출해서 확인
- Helm render: kube-prometheus-stack, Loki, Alloy chart를 pinned version과 values로 렌더링
- Live cluster check: CRD, monitoring namespace resource, dashboard ConfigMap, webhook Secret, kube-prometheus-stack Pod readiness, Loki/Alloy, app namespace backend service/port/readiness를 `kubectl`로 확인

### Discord Webhook Secret

Discord webhook URL은 repo에 평문으로 커밋하지 않습니다. SealedSecrets controller가 설치된 클러스터에서 운영자가 다음 흐름으로 SealedSecret을 생성합니다.

```sh
mkdir -p kubernetes/monitoring/secrets

kubectl -n monitoring create secret generic alertmanager-contact-points \
  --from-literal=webhook-url="$ALERT_WEBHOOK_URL" \
  --dry-run=client -o yaml \
  | kubeseal --controller-namespace kube-system --format yaml \
  > kubernetes/monitoring/secrets/alertmanager-contact-points.sealedsecret.yaml

kubectl apply -f kubernetes/monitoring/secrets/alertmanager-contact-points.sealedsecret.yaml
```

SealedSecret 파일은 cluster 공개키로 암호화된 값만 포함합니다. controller namespace가 다르면 `--controller-namespace`를 실제 설치 namespace로 바꿉니다.
