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

`/metrics`와 `/api/health` 요청은 API request rate/latency metric과 request completion log에서 제외합니다.

### Logs

backend는 `X-Request-ID`를 수용하고, 없으면 request ID를 생성한 뒤 응답 header로 반환합니다.

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

민감 정보는 로그에 싣지 않습니다. token, password, cookie, OAuth secret, authorization header, 제출 source code는 저장 대상이 아닙니다.

frontend nginx의 Kubernetes 설정은 access log를 `/dev/stdout`, error log를 `/dev/stderr`로 출력합니다.

Kubernetes Pod 로그 수집은 Grafana Alloy와 Loki로 처리합니다. 클라우드 object storage를 사용할 수 없는 현재 운영 조건에서는 Loki를 Monolithic mode로 배포하고 Longhorn PVC 기반 filesystem storage를 사용합니다.

- Loki release: `loki`, namespace: `monitoring`.
- Alloy release: `alloy`, namespace: `monitoring`.
- Loki storage: `filesystem` on Longhorn PVC.
- Loki retention: `code-place-dev` 3일, `code-place-prod` 7일.
- 수집 namespace: `code-place-dev`, `code-place-prod`, `monitoring`.
- Grafana datasource: 기존 kube-prometheus-stack Grafana에 `Loki` datasource를 추가합니다.

이 구성은 클라우드 없는 단기 retention 기준선입니다. prod 로그량이 커지거나 로그 저장소 장애 도메인을 더 분리해야 하면, Loki는 내부에서 별도 운영하는 S3 호환 object storage, 예를 들어 독립 MinIO cluster, 로 이전합니다. Grafana Loki chart의 내장 MinIO subchart는 신규 운영 의존성으로 사용하지 않습니다.

### Tracing

OpenTelemetry는 앱 초기화 코드에 내장되어 있지만 기본값은 `OTEL_ENABLED=0`입니다. dev/staging에서 먼저 활성화하고 collector/Tempo/sampling 확인 후 prod 활성화를 결정합니다.

자동 계측 대상은 Django, requests, psycopg2, Redis, Celery입니다. 제출/채점 경로에는 manual span을 추가합니다.

- `judge_task`
- `submission.judge`
- `judge_server.request`

기본 sampling 값은 `OTEL_TRACES_SAMPLER_ARG=0.05`입니다.

현재 Kubernetes manifest에는 backend/celery의 `OTEL_EXPORTER_OTLP_ENDPOINT`가 `http://otel-collector.monitoring.svc.cluster.local:4317`로 잡혀 있습니다. 다만 `otel-collector`와 Tempo는 아직 배포 리소스로 포함하지 않습니다. 다음 조건이 정해지기 전에는 `OTEL_ENABLED=1`을 켜지 않습니다.

- trace 저장 backend: Tempo 단일 binary, Tempo distributed, 외부 managed backend 중 선택.
- retention: dev/prod별 trace 보관 기간과 저장 용량.
- storage: filesystem, S3 호환 object storage, Longhorn PVC 중 선택.
- sampling: dev/prod sampling ratio와 error trace 우선 보존 정책.
- Grafana datasource: Tempo datasource 이름과 dashboard trace link 규칙.

이 조건이 정해진 뒤 `otel-collector`와 Tempo를 `kubernetes/monitoring` 하위 Helm values 또는 별도 kustomize 리소스로 추가합니다.

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
- `validate.sh`: monitoring YAML, Grafana dashboard JSON, kustomize render, 선택적 promtool/Helm render 검증 스크립트.
- `kustomization.yaml`: 기존 `monitoring` namespace의 kube-prometheus-stack/Grafana/Alertmanager에 붙일 CodePlace monitoring 리소스 묶음.

`alertmanager-contact-points` Secret은 repo에 저장하지 않습니다. backend의 `/data/config/secret.key`와 같은 비밀값이지만, 자동으로 파일이 생기는 구조는 아닙니다. 운영자가 `kubectl create secret`으로 만들거나 ExternalSecrets/SealedSecrets 같은 Secret 주입 도구로 생성해야 합니다. AlertmanagerConfig는 generic webhook이 아니라 Prometheus Operator의 native `discordConfigs`를 사용합니다.

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
- `LokiUnavailable`: Loki single-binary Pod not ready 1분 지속.

### P1

P1은 `group_wait=30s`, `repeat_interval=1h`로 전달합니다.

- `ApiLatencyHigh`: p95 latency 2초 초과 5분 지속.
- `JudgeWaitingQueueBacklog`: `waiting_queue` 5 초과 3분 지속.
- `CeleryWorkerRestarting`: worker restart 3회 이상/15분.
- `CeleryBeatDown`: beat Pod not ready 2분 지속.
- `PodCrashLooping`: 주요 Pod restart 증가 5분 지속.
- `CodePlacePodNotReady`: 주요 앱/DB/Redis Pod not ready 5분 지속.
- `CodePlaceContainerCPUHigh`: 주요 컨테이너 CPU limit 사용률 80% 초과 10분 지속.
- `CodePlaceContainerMemoryHigh`: 주요 컨테이너 memory limit 사용률 85% 초과 10분 지속.
- `PVCAlmostFull`: PVC 사용률 85% 초과 10분 지속.
- `LokiPVCAlmostFull`: Loki Longhorn PVC 사용률 85% 초과 10분 지속.
- `AlloyDaemonSetUnavailable`: Alloy log collector가 모든 node에서 available하지 않음 5분 지속.
- `LokiGatewayUnavailable`: Loki gateway Pod not ready 2분 지속.
- `CodePlaceNodePressure`: node memory/disk/PID pressure 5분 지속.

## 5. 운영 확인 절차

1. kube-prometheus-stack을 `monitoring` namespace에 설치하거나 업그레이드할 때 `kubernetes/monitoring/kube-prometheus-stack-values.yaml`을 함께 적용합니다. 이 값 파일이 `monitoring.code-place-dev.site` Grafana ingress와 dashboard sidecar 설정까지 관리합니다. Prometheus Operator CRD가 `AlertmanagerConfig.discordConfigs`를 지원하는 버전인지 확인합니다.
2. `alertmanager-contact-points` Secret을 운영 클러스터의 `monitoring` namespace에 생성합니다. 이 값은 Kubernetes Secret으로 참조되며, Pod 파일로 mount하지 않습니다.
3. Loki와 Alloy를 설치합니다.
   - `helm upgrade --install loki grafana-community/loki --namespace monitoring --values kubernetes/monitoring/logs/loki-values.yaml`
   - `helm upgrade --install alloy grafana/alloy --namespace monitoring --values kubernetes/monitoring/logs/alloy-values.yaml`
4. 애플리케이션은 환경별 overlay로 적용합니다.
   - dev: `kubectl apply -k kubernetes/overlays/dev`
   - prod: `kubectl apply -k kubernetes/overlays/prod`
5. CodePlace monitoring 리소스는 기존 kube-prometheus-stack이 있는 클러스터에 별도로 적용합니다.
   - `kubectl apply -k kubernetes/monitoring`
6. Prometheus target에서 `backend` ServiceMonitor가 healthy인지 확인합니다.
7. Grafana의 `CodePlace Overview` dashboard에서 request rate, 5xx, latency, submission status, waiting queue, judge heartbeat, Pod readiness/restart, CPU/memory, PVC, PostgreSQL/Redis readiness panel을 확인합니다.
8. Grafana의 `CodePlace Logs` dashboard에서 Loki ready, Alloy node coverage, Loki PVC usage, 최근 backend error, judge/celery log panel을 확인합니다.
9. Grafana Explore에서 `Loki` datasource를 선택하고 `{namespace="code-place-dev"}` 쿼리가 로그를 반환하는지 확인합니다.
10. test alert 또는 임시 rule로 P0 webhook 수신 시간이 1분 이내인지 확인합니다.

운영 적용 전제는 다음과 같습니다.

- `/metrics`는 cluster 내부 scrape 전용이며 외부 Ingress에 노출하지 않습니다.
- Discord webhook URL은 Git에 저장하지 않습니다.
- Docker Swarm monitoring 구성은 레거시로 유지하고 신규 관측성 리소스와 분리합니다.
- OpenTelemetry는 `OTEL_ENABLED=0` 기본값을 유지하고 dev/staging에서 먼저 활성화합니다.
- P0/P1 알림 라우팅은 AlertmanagerConfig로 관리하며 Grafana UI 수동 설정에 의존하지 않습니다.
- 로그 수집은 Grafana Alloy와 Loki로 관리하며 Promtail은 신규 도입하지 않습니다.
- PostgreSQL/Redis 세부 지표는 별도 exporter 없이 kube-state-metrics/kubelet 기반 readiness, restart, PVC 관측부터 제공합니다. connection, lock, Redis memory/client 같은 상세 지표는 exporter 도입 이후 확장합니다.
- Sentry backend SDK는 기본 PII 자동 전송을 비활성화합니다. 사용자 영향 분석은 Sentry event와 request_id 기반 backend JSON log를 함께 사용합니다.
- Tempo tracing은 저장소/retention 결정을 먼저 요구하므로 현재 PR에서는 켜지 않습니다.

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

`promtool`이 있는 환경에서는 `promtool check rules kubernetes/monitoring/prometheus-rules.yaml`도 실행합니다.
`helm`이 있는 환경에서는 Loki/Alloy values를 `helm template`로 렌더링 검증합니다.

### Discord Webhook Secret

Discord webhook URL은 repo에 커밋하지 않습니다. 클러스터별로 다음 명령으로 생성합니다.

```sh
kubectl -n monitoring create secret generic alertmanager-contact-points \
  --from-literal=webhook-url="$ALERT_WEBHOOK_URL" \
  --dry-run=client -o yaml | kubectl apply -f -
```
