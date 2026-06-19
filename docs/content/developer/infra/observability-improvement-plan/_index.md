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

- **User Path:** Traefik/Ingress, frontend nginx, backend Django API.
- **Submission/Judge Path:** submission 생성, Celery `judge_task`, Redis `waiting_queue`, judge-server heartbeat, judge-server `/judge` 호출, 결과 저장.
- **Async Jobs:** celery-worker, celery-beat, scheduled tasks.
- **Data Stores:** PostgreSQL/CNPG, Redis Sentinel.
- **Platform:** backend/frontend/celery/judge Pod, node, PVC.
- **Client/Error:** frontend runtime error, backend exception, request ID 기반 로그.

## 2. 구현 내용

### Metrics

backend는 `django-prometheus` 기반 `/metrics` 엔드포인트를 제공합니다. 이 엔드포인트는 ServiceMonitor가 cluster 내부에서 scrape하며 외부 Ingress에는 연결하지 않습니다.

추가된 CodePlace custom metrics는 다음과 같습니다.

- `codeplace_http_requests_total{method,endpoint,status_code}`
- `codeplace_http_request_duration_seconds{method,endpoint}`
- `codeplace_submission_status_count{status}`
- `codeplace_submission_judge_duration_seconds`
- `codeplace_waiting_queue_length`
- `codeplace_judge_server_available{hostname}`
- `codeplace_judge_server_last_heartbeat_age_seconds{hostname}`
- `codeplace_judge_server_task_number{hostname}`
- `codeplace_celery_task_count{task_name,status}`
- `codeplace_celery_task_runtime_seconds{task_name}`
- `codeplace_celery_task_last_runtime_seconds{task_name,status}`

`/metrics`와 `/api/health` 요청은 API request rate/latency metric과 request completion log에서 제외합니다.

### Logs

backend는 `X-Request-ID`를 수용하고, 없으면 request ID를 생성한 뒤 응답 header로 반환합니다. Frontend axios 요청은 `X-Request-ID`를 생성해 backend로 전달하고, backend가 반환한 request ID를 axios response/error와 Sentry request context에 보존합니다. API 요청에서 Celery task를 enqueue할 때 request ID를 Celery header로 전파하고, worker 실행 중 같은 request ID를 JSON log context에 복원합니다.

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

민감 정보는 로그에 싣지 않습니다. token, password, cookie, OAuth secret, authorization header, 제출 source code는 저장 대상이 아닙니다. OpenTelemetry가 활성화된 요청/작업 로그에는 현재 span의 `trace_id`, `span_id`를 추가해 Tempo trace와 Loki JSON log를 연결합니다.

frontend nginx의 Kubernetes 설정은 access log를 `/dev/stdout`, error log를 `/dev/stderr`로 출력합니다. access log는 Loki에서 파싱 가능한 JSON 형식이며, `request_id`, `method`, `path`, `status_code`, `duration_seconds`, `remote_addr`, `user_agent`, `x_forwarded_for`를 포함합니다. nginx는 들어온 `X-Request-ID`를 유지하고, 없으면 nginx `$request_id`를 생성해 응답 header와 backend proxy header로 전달합니다.

Kubernetes Pod 로그 수집은 Grafana Alloy와 Loki로 처리합니다. 클라우드 object storage를 사용할 수 없는 현재 운영 조건에서는 Loki를 Monolithic mode로 배포하고 Longhorn PVC 기반 filesystem storage를 사용합니다.

- Loki release: `loki`, namespace: `monitoring`.
- Alloy release: `alloy`, namespace: `monitoring`.
- Loki storage: `filesystem` on Longhorn PVC.
- Loki retention: `code-place-dev` 3일, `code-place-prod` 7일.
- 수집 namespace: `code-place-dev`, `code-place-prod`, `monitoring`.
- Grafana datasource: 기존 kube-prometheus-stack Grafana에 `Loki` datasource를 추가합니다.

이 구성은 클라우드 없는 단기 retention 기준선입니다. Longhorn PVC는 hostPath/emptyDir보다 낫습니다. Kubernetes에서 lifecycle을 관리할 수 있고, PVC 사용률과 Longhorn volume health를 운영자가 볼 수 있기 때문입니다. 다만 durable log archive는 아니므로 장애 분석용 단기 저장소로만 취급합니다.

현재 유지해야 하는 로그 저장소 불변 조건은 다음과 같습니다.

- Loki deployment mode는 `Monolithic`입니다.
- Loki storage type은 `filesystem`입니다.
- Loki PVC storageClass는 `longhorn`, size는 `50Gi`입니다.
- Loki retention은 dev 72h, prod 168h입니다.
- Grafana Loki chart의 내장 MinIO subchart는 사용하지 않습니다.

prod 로그량이 커지면 먼저 noisy log를 줄이거나 retention을 줄입니다. 그래도 부족하면 Longhorn replica 상태와 node 여유 disk를 확인한 뒤 PVC를 증설합니다. 로그 저장소 장애 도메인을 더 분리해야 하면, Loki는 내부에서 별도 운영하는 S3 호환 object storage, 예를 들어 독립 MinIO cluster, 로 이전합니다.

### Tracing

OpenTelemetry는 앱 초기화 코드에 내장되어 있고, base/prod 기본값은 `OTEL_ENABLED=0`입니다. dev overlay에서만 `OTEL_ENABLED=1`로 켜서 collector/Tempo/sampling을 먼저 확인합니다.

자동 계측 대상은 Django, requests, psycopg2, Redis, Celery입니다. 제출/채점 경로에는 manual span을 추가합니다.

- `judge_task`
- `submission.judge`
- `judge_server.request`

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

- `backend-service-monitor.yaml`: backend `/metrics` scrape, interval 15s.
- `prometheus-rules.yaml`: P0/P1 fast alert rules.
- `alertmanager-config.yaml`: P0/P1 Discord alert routing.
- `grafana-dashboard-codeplace.yaml`: CodePlace overview dashboard. `namespace` 변수로 `code-place-dev`와 `code-place-prod`를 분리해서 조회합니다.
- `kube-prometheus-stack-values.yaml`: Prometheus/Alertmanager selector, evaluation interval, shared Grafana ingress와 dashboard sidecar 설정.
- `logs/loki-values.yaml`: Loki Monolithic, Longhorn PVC, dev/prod retention 설정.
- `logs/alloy-values.yaml`: Alloy DaemonSet 기반 Kubernetes Pod log collection 설정.
- `grafana-dashboard-logs.yaml`: Loki/Alloy health, Loki PVC, 최근 backend error, judge/celery log 조회 dashboard.
- `otel-collector.yaml`: backend/celery OTLP trace를 받아 Tempo로 전송하는 OpenTelemetry Collector.
- `tempo.yaml`: Tempo single binary, Longhorn PVC 기반 trace 저장소.
- `grafana-dashboard-traces.yaml`: Collector/Tempo readiness, span ingest/export, Tempo PVC usage dashboard.
- `validate.sh`: monitoring YAML, Grafana dashboard JSON, kustomize render, 선택적 promtool/Helm render 검증 스크립트.
- `kustomization.yaml`: 기존 `monitoring` namespace의 kube-prometheus-stack/Grafana/Alertmanager에 붙일 CodePlace monitoring 리소스 묶음.

`alertmanager-contact-points` Secret은 repo에 저장하지 않습니다. backend의 `/data/config/secret.key`와 같은 비밀값이지만, 자동으로 파일이 생기는 구조는 아닙니다. 운영자가 `kubectl create secret`으로 만들거나 ExternalSecrets/SealedSecrets 같은 Secret 주입 도구로 생성해야 합니다. AlertmanagerConfig는 generic webhook이 아니라 Prometheus Operator의 native `discordConfigs`를 사용합니다.

Email fallback은 SMTP host/from/to/auth가 필요하므로 기본 kustomization에는 포함하지 않습니다. SMTP 값이 정해지면 `kubernetes/monitoring/alertmanager-config-email.example.yaml`을 실제 값으로 복사하거나 패치해서 적용합니다. Prometheus Operator의 `AlertmanagerConfig`는 receiver에 `emailConfigs`를 지원하며, SMTP password는 같은 namespace의 Secret key로 참조합니다.

## 4. 빠른 알림 정책

### P0

P0는 `group_wait=10s`, `repeat_interval=15m`로 Discord에 빠르게 전달합니다.

- `BackendTargetDown`: backend scrape 실패 1분 지속.
- `Api5xxSpike`: backend 5xx 비율 5% 초과 2분 지속.
- `Ingress5xxSpike`: Traefik 5xx 비율 5% 초과 2분 지속.
- `JudgeAllUnavailable`: 사용 가능한 judge-server 0개 1분 지속.
- `JudgeHeartbeatCritical`: judge heartbeat age 180초 초과.
- `PostgresUnavailable`: PostgreSQL Pod not ready 1분 지속.
- `RedisUnavailable`: Redis Pod not ready 1분 지속.
- `PostgresExporterDown`: CNPG PostgreSQL exporter metric 수집 실패 2분 지속.
- `RedisExporterDown`: Redis exporter metric 수집 실패 2분 지속.
- `LokiUnavailable`: Loki single-binary Pod not ready 1분 지속.

### P1

P1은 `group_wait=30s`, `repeat_interval=1h`로 전달합니다.

- `ApiLatencyHigh`: p95 latency 2초 초과 5분 지속.
- `JudgeWaitingQueueBacklog`: `waiting_queue` 5 초과 3분 지속.
- `CeleryWorkerRestarting`: worker restart 3회 이상/15분.
- `CeleryBeatDown`: beat Pod not ready 2분 지속.
- `CeleryTaskFailures`: task failure 발생 2분 지속.
- `CeleryTaskRetries`: task retry 3회 초과/10분, 5분 지속.
- `CeleryTaskRuntimeHigh`: task p95 runtime 120초 초과 10분 지속.
- `PodCrashLooping`: 주요 Pod restart 증가 5분 지속.
- `CodePlacePodNotReady`: 주요 앱/DB/Redis Pod not ready 5분 지속.
- `CodePlaceContainerCPUHigh`: 주요 컨테이너 CPU limit 사용률 80% 초과 10분 지속.
- `CodePlaceContainerMemoryHigh`: 주요 컨테이너 memory limit 사용률 85% 초과 10분 지속.
- `PostgresCollectorError`: CNPG PostgreSQL metrics collection error 5분 지속.
- `PostgresHADegraded`: PostgreSQL instance가 3개 node에 분산되지 않음 10분 지속.
- `RedisMemoryHigh`: Redis memory 사용률 85% 초과 10분 지속.
- `PVCAlmostFull`: PVC 사용률 85% 초과 10분 지속.
- `LokiPVCAlmostFull`: Loki Longhorn PVC 사용률 85% 초과 10분 지속.
- `AlloyDaemonSetUnavailable`: Alloy log collector가 모든 node에서 available하지 않음 5분 지속.
- `LokiGatewayUnavailable`: Loki gateway Pod not ready 2분 지속.
- `OTelCollectorUnavailable`: OpenTelemetry Collector Pod not ready 2분 지속.
- `TempoUnavailable`: Tempo Pod not ready 2분 지속.
- `TempoPVCAlmostFull`: Tempo PVC 사용률 85% 초과 10분.
- `CodePlaceNodePressure`: node memory/disk/PID pressure 5분 지속.

## 5. 운영 확인 절차

1. kube-prometheus-stack을 `monitoring` namespace에 설치하거나 업그레이드할 때 `kubernetes/monitoring/kube-prometheus-stack-values.yaml`을 함께 적용합니다. 이 값 파일이 `monitoring.code-place-dev.site` Grafana ingress와 dashboard sidecar 설정까지 관리합니다. Prometheus Operator CRD가 `AlertmanagerConfig.discordConfigs`를 지원하는 버전인지 확인합니다.
2. `alertmanager-contact-points` Secret을 운영 클러스터의 `monitoring` namespace에 생성합니다. 이 값은 Kubernetes Secret으로 참조되며, Pod 파일로 mount하지 않습니다.
   Email fallback을 켤 경우 SMTP 정보를 별도로 정한 뒤 `alertmanager-email` Secret과 email AlertmanagerConfig를 추가 적용합니다.
3. Loki와 Alloy를 설치합니다.
   - `helm upgrade --install loki grafana-community/loki --namespace monitoring --values kubernetes/monitoring/logs/loki-values.yaml`
   - `helm upgrade --install alloy grafana/alloy --namespace monitoring --values kubernetes/monitoring/logs/alloy-values.yaml`
4. 애플리케이션은 환경별 overlay로 적용합니다.
   - dev: `kubectl apply -k kubernetes/overlays/dev`
   - prod: `kubectl apply -k kubernetes/overlays/prod`
5. CodePlace monitoring 리소스는 기존 kube-prometheus-stack이 있는 클러스터에 별도로 적용합니다.
   - `kubectl apply -k kubernetes/monitoring`
6. Prometheus target에서 `backend` ServiceMonitor가 healthy인지 확인합니다.
7. Grafana의 `CodePlace Overview` dashboard에서 request rate, 5xx, latency, submission status, waiting queue, judge heartbeat, Celery task throughput/runtime, Pod readiness/restart, CPU/memory, PVC, PostgreSQL/Redis readiness panel을 확인합니다.
8. Grafana의 `CodePlace Logs` dashboard에서 Loki ready, Alloy node coverage, Loki PVC usage, 최근 backend error, frontend 4xx/5xx, judge/celery log panel을 확인합니다.
9. Grafana의 `CodePlace Logs` dashboard에서 `request_id` 변수에 실제 응답 header 또는 JSON log의 request ID를 넣고 해당 요청 로그가 좁혀지는지 확인합니다.
10. Grafana의 `CodePlace Traces` dashboard에서 Tempo ready, OTel Collector ready, trace receive/export rate, Tempo PVC usage를 확인합니다.
11. Grafana Explore에서 `Loki` datasource를 선택하고 `{namespace="code-place-dev"}` 쿼리가 로그를 반환하는지 확인합니다.
12. Grafana Explore에서 `Tempo` datasource를 선택하고 `service.name=codeplace-backend` 또는 `service.name=codeplace-celery` trace가 조회되는지 확인합니다.
13. test alert 또는 임시 rule로 P0 webhook 수신 시간이 1분 이내인지 확인합니다.

운영 적용 전제는 다음과 같습니다.

- `/metrics`는 cluster 내부 scrape 전용이며 외부 Ingress에 노출하지 않습니다.
- Discord webhook URL은 Git에 저장하지 않습니다.
- Docker Swarm monitoring 구성은 레거시로 유지하고 신규 관측성 리소스와 분리합니다.
- OpenTelemetry는 base/prod `OTEL_ENABLED=0` 기본값을 유지하고 dev overlay에서 먼저 활성화합니다.
- P0/P1 알림 라우팅은 AlertmanagerConfig로 관리하며 Grafana UI 수동 설정에 의존하지 않습니다.
- 로그 수집은 Grafana Alloy와 Loki로 관리하며 Promtail은 신규 도입하지 않습니다.
- PostgreSQL은 CNPG instance exporter와 PodMonitor로 `cnpg_collector_*` 지표를 수집합니다. Redis는 Opstree Redis exporter sidecar와 PodMonitor로 `redis_*` 지표를 수집합니다.
- Sentry backend SDK는 기본 PII 자동 전송을 비활성화하고 전송 직전 `authorization`, `cookie`, `password`, `token`, `secret`, 제출 source code 계열 필드를 redaction합니다. 사용자 영향 분석은 Sentry event와 request_id 기반 backend JSON log를 함께 사용합니다.
- Frontend는 axios 요청마다 `X-Request-ID`를 전파하고 마지막 request ID를 `window.__CODEPLACE_LAST_REQUEST_ID__`와 Sentry request context에 저장합니다.
- Frontend Sentry 설정은 빌드 시점 값입니다. `APP_VERSION`, `SENTRY_ENVIRONMENT`, `SENTRY_DSN`, `USE_SENTRY`는 frontend image build-arg로 주입하며, Kubernetes Deployment의 런타임 env만 변경해도 이미 빌드된 JS bundle에는 반영되지 않습니다.
- Backend/Celery Sentry release는 `SENTRY_RELEASE` env가 있으면 사용합니다. 이미지 태그와 동일한 commit SHA를 넣어 Grafana/Loki/Sentry 간 배포 기준을 맞추는 것을 권장합니다.
- Tempo tracing은 monitoring namespace에 배포하지만, prod app trace export는 dev 확인 후 별도 승격합니다.

## 6. 검증

로컬 검증 항목은 다음과 같습니다.

- Python compile: `python3 -m compileall backend/account backend/judge backend/oj backend/utils`
- Django check: `/tmp/code-place-backend-venv/bin/python manage.py check --settings=oj.settings`
- Metrics endpoint: Django test client 기준 `/metrics` 200 및 `codeplace_*` metric 포함 확인
- Kubernetes app render: `kubectl kustomize kubernetes/overlays/dev`, `kubectl kustomize kubernetes/overlays/prod`
- Kubernetes monitoring render: `kubectl kustomize kubernetes/monitoring`
- Logs values YAML parse: `kubernetes/monitoring/logs/loki-values.yaml`, `kubernetes/monitoring/logs/alloy-values.yaml`
- Grafana dashboard JSON parse: `grafana-dashboard-codeplace.yaml`, `grafana-dashboard-logs.yaml`
- Monitoring bundle validation: `bash kubernetes/monitoring/validate.sh`
  - YAML parse: kube-prometheus-stack values, PrometheusRule, AlertmanagerConfig, ServiceMonitor, PodMonitor, Loki/Alloy values.
  - Grafana dashboard JSON parse와 dashboard shape check: uid/title/refresh/panel/target expr.
  - PrometheusRule shape check: P0/P1 interval, alert priority/severity, summary/description, duplicate alert namespace label.
  - AlertmanagerConfig shape check: groupBy, P0/P1 Discord receivers, webhook Secret reference.
  - kube-prometheus-stack values shape check: Prometheus selector policy, AlertmanagerConfig selector, Loki datasource, dashboard sidecar label.
  - Loki storage shape check: Monolithic mode, filesystem storage, Longhorn PVC, 50Gi size, dev/prod retention, MinIO disabled.
  - scrape resource shape check: ServiceMonitor/PodMonitor selector label, scrape path/port/interval.
  - Monitoring kustomization shape check: email fallback example이 기본 적용에 섞이지 않는지 확인.
- Live cluster smoke check: `bash kubernetes/monitoring/smoke-check.sh`
  - Prometheus Operator CRD, monitoring namespace resource, selector label, webhook Secret, kube-prometheus-stack Pod readiness, optional Loki/Alloy, app namespace backend service/port/readiness를 읽기 전용으로 확인합니다.

`promtool`이 있는 환경에서는 `promtool check rules kubernetes/monitoring/prometheus-rules.yaml`도 실행합니다.
`helm`이 있는 환경에서는 Loki/Alloy values를 `helm template`로 렌더링 검증합니다.

### Discord Webhook Secret

Discord webhook URL은 repo에 커밋하지 않습니다. 클러스터별로 다음 명령으로 생성합니다.

```sh
kubectl -n monitoring create secret generic alertmanager-contact-points \
  --from-literal=webhook-url="$ALERT_WEBHOOK_URL" \
  --dry-run=client -o yaml | kubectl apply -f -
```
