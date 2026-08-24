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

- **User Path:** public HTTPS probe, Traefik/Ingress, frontend nginx, backend Django API.
- **Submission/Judge Path:** submission 생성, Celery `judge_task`, Redis `waiting_queue`, judge-server heartbeat, judge-server `/judge` 호출, 결과 저장.
- **Async Jobs:** celery-worker, celery-beat, scheduled tasks.
- **Data Stores:** PostgreSQL/CNPG, Redis Sentinel.
- **Platform:** backend/frontend/celery/judge Pod, node, PVC, monitoring stack.
- **Client/Error:** frontend runtime error, backend exception, request ID 기반 로그.

## 2. 구현 내용

### Metrics

backend는 `django-prometheus` 기반 `/metrics` 엔드포인트를 제공합니다. 이 엔드포인트는 ServiceMonitor가 cluster 내부에서 scrape하며 외부 Ingress에는 연결하지 않습니다.

추가된 CodePlace custom metrics는 다음과 같습니다.

- `codeplace_http_requests_total{method,endpoint,status_code}`
- `codeplace_http_request_duration_seconds{method,endpoint}`
- `codeplace_submission_create_outcome_total{status,scope}`
- `codeplace_judge_task_outcome_total{status,scope}`
- `codeplace_waiting_queue_length`
- `codeplace_celery_broker_queue_length`
- `codeplace_collector_success{collector}`
- `codeplace_redis_sentinel_health{check}`

Celery worker에서 발생한 judge outcome은 worker 프로세스 메모리가 아니라 Redis hash에 누적하고 backend `/metrics` collector가 노출합니다. 모든 backend replica가 동일한 공유 counter를 노출하므로 비율은 replica를 더하지 않고 `avg by (namespace, scope, status)`로 중복 제거하며, 실패 여부는 `max by (namespace, scope, status)`로 판정합니다. Collector가 Redis 값을 읽지 못하면 queue 값을 `0`으로 대체하지 않고 해당 시계열을 생략한 뒤 `codeplace_collector_success=0`을 노출합니다.

`/metrics`와 `/api/health` 요청은 API request rate/latency metric과 request completion log에서 제외합니다.

### Logs

backend는 `X-Request-ID`를 수용하고, 없으면 request ID를 생성한 뒤 응답 header로 반환합니다.

Submission API는 동일한 request ID를 Celery task header로 전달하고 worker task context에 bind합니다. 따라서 HTTP 요청 로그와 비동기 judge 로그를 같은 ID로 조회할 수 있습니다.

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

브라우저 runtime exception은 Sentry가 수집합니다. CI frontend build는 배포 `APP_VERSION`과 같은 Sentry release에 source map을 업로드하고, 업로드 후 image에서 `.map` 파일을 제거합니다. `SENTRY_AUTH_TOKEN`은 GitHub Actions BuildKit secret으로만 전달합니다.

Pod 로그 수집은 Grafana Alloy와 Loki로 처리합니다. 클라우드 object storage를 사용할 수 없는 현재 조건에서는 Loki SingleBinary + Longhorn PVC를 단기 보관 기준선으로 둡니다.

- dev log retention: 3일.
- prod log retention: 7일.
- 수집 대상: `code-place-dev`, `code-place-prod`, `monitoring`, Traefik Pod.

### Tracing

OpenTelemetry는 앱 초기화 코드에 내장되어 있습니다. base manifest는 안전한 기본값으로 `OTEL_ENABLED=0`을 유지하지만, dev와 prod overlay는 모두 `OTEL_ENABLED=1`로 활성화합니다. dev는 `OJ_ENV=dev`와 `OTEL_DEPLOYMENT_ENVIRONMENT=dev`, prod는 `OJ_ENV=production`과 `OTEL_DEPLOYMENT_ENVIRONMENT=prod`를 명시해 Django 실행 환경과 trace resource 환경을 독립적으로 고정합니다. backend, celery-worker, celery-beat는 각각 고정된 `OTEL_SERVICE_NAME`을 사용하므로 Django가 Celery app을 먼저 import해도 service identity가 바뀌지 않습니다.

계측 초기화 실패는 애플리케이션 기동 실패로 전파하지 않고 구조화 오류 로그를 남긴 뒤 fail-open 처리합니다. dev와 prod trace는 동일한 Collector/Tempo 경로를 사용하되 Grafana TraceQL에서 `deployment.environment`로 분리합니다.

자동 계측 대상은 Django, requests, psycopg2, Redis, Celery입니다. 제출/채점 경로에는 manual span을 추가합니다.

- `judge_task`
- `submission.judge`
- `judge_server.request`

기본 sampling 값은 `OTEL_TRACES_SAMPLER_ARG=0.05`입니다.

## 3. Kubernetes Monitoring

신규 monitoring 리소스는 `kubernetes/monitoring` 아래에 두고, 애플리케이션 `dev/prod` overlay에 포함하지 않습니다.

- `backend-service-monitor.yaml`: backend `/metrics` scrape, interval 15s.
- `blackbox-exporter.yaml`, `public-endpoint-probes.yaml`: frontend/hub-auth/Grafana 공개 HTTPS probe.
- `datastore-pod-monitors.yaml`: CNPG/Redis exporter scrape.
- `traefik-pod-monitor.yaml`: K3s Traefik Pod의 `metrics` port 직접 scrape.
- `dcgm-exporter.yaml`: GPU 상태 metric과 scrape target.
- `otel-collector.yaml`, `tempo.yaml`: dev/prod trace 수집, 전달, 저장 경로.
- `logs/loki-values.yaml`, `logs/alloy-values.yaml`: Loki/Alloy Helm values.
- `prometheus-rules.yaml`: P0/P1 fast alert rules와 일부 recording rules.
- `alertmanager-config.yaml`: P0/P1 Discord alert routing.
- `grafana-dashboard-codeplace.yaml`: 환경별 서비스 SLI와 핵심 현재 상태를 보여주는 CodePlace overview dashboard.
- `grafana-dashboard-platform.yaml`: 환경별 workload, resource, PostgreSQL, Redis 상세 진단 dashboard.
- `grafana-dashboard-ai-api.yaml`: `prod`/`dev`를 선택하는 AI API outcome/latency dashboard.
- `grafana-dashboard-ai-inference.yaml`: prod 전용 vLLM/GPU runtime dashboard.
- `grafana-dashboard-logs.yaml`: 환경별 앱 로그와 request ID 조사 dashboard.
- `grafana-dashboard-log-pipeline.yaml`: cluster-global Loki/Alloy 수집 경로 상태 dashboard.
- `grafana-dashboard-kubernetes-events.yaml`: 환경별 Pod 상태와 Warning event dashboard.
- `grafana-dashboard-monitoring-stack.yaml`: 필수 scrape 경로의 `ABSENT`/`DOWN`/`UP` 상태 dashboard.
- `grafana-dashboard-public-endpoints.yaml`: 환경별 frontend/hub-auth 공개 probe dashboard.
- `grafana-dashboard-storage.yaml`: 환경별 PVC와 cluster-global Longhorn 상태 dashboard.
- `grafana-dashboard-traces.yaml`: 환경별 backend/celery trace와 Collector/Tempo 상태 dashboard.
- `kube-prometheus-stack-values.yaml`: Prometheus/Alertmanager selector, evaluation interval, CRD upgrade hook, shared Grafana ingress와 dashboard sidecar 설정.
- `kustomization.yaml`: 기존 `monitoring` namespace의 kube-prometheus-stack/Grafana/Alertmanager에 붙일 CodePlace monitoring 리소스 묶음.

환경별 dashboard는 단일 `environment=prod,dev` 변수로 조회 범위를 고정하고 `All` 선택을 제공하지 않습니다. prod 전용 vLLM/GPU runtime과 cluster-global log pipeline은 별도 dashboard로 분리해 서로 다른 범위의 graph가 한 화면에 섞이지 않도록 합니다. 전체 dashboard는 11개이며, 공통 dashboard dropdown은 변수와 시간 범위를 유지합니다. cluster-global panel은 제목과 설명에 범위를 명시합니다.

Grafana는 단일 Longhorn `ReadWriteOnce` PVC를 사용하므로 upgrade 전략을 `Recreate`로 고정합니다. `RollingUpdate`로 바꾸면 기존 Pod가 volume을 점유한 상태에서 새 Pod가 대기해 Helm atomic upgrade가 실패할 수 있습니다.

`alertmanager-contact-points` Secret은 repo에 평문으로 저장하지 않습니다. 운영자는 SealedSecret으로 `monitoring` namespace에 생성합니다. AlertmanagerConfig는 generic webhook이 아니라 Prometheus Operator의 native `discordConfigs`를 사용합니다.

## 4. 빠른 알림 정책

### P0

P0는 `group_wait=10s`, `repeat_interval=15m`로 Discord에 빠르게 전달합니다.

- `TraefikScrapeUnavailable`: Traefik target 부재 또는 scrape 실패 1분 지속.
- `AlloyScrapeUnavailable`: Alloy target 부재 또는 scrape 실패 1분 지속.
- `BackendTargetDown`: backend scrape 실패 1분 지속.
- `Api5xxSpike`: backend 5xx 비율 5% 초과 2분 지속.
- `Ingress5xxSpike`: Traefik 5xx 비율 5% 초과 2분 지속.
- `PublicEndpointDown`: prod frontend 또는 hub-auth HTTPS probe의 실제 실패 1분 지속. 실패한 service와 URL을 알림에 표시.
- `PostgresUnavailable`: PostgreSQL Pod not ready 또는 readiness metric missing 1분 지속.
- `PostgresPrimaryUnavailable`: `postgres-rw` ready endpoint 부재 1분 지속.
- `RedisUnavailable`: Redis/Sentinel Pod not ready 또는 readiness metric missing 1분 지속.
- `RedisSentinelUnavailable`: Sentinel master 탐색 또는 quorum 검사 실패 1분 지속.
- `LokiUnavailable`: Loki Pod not ready 1분 지속.
- `DCGMExporterUnavailable`: GPU metric target 부재 또는 scrape 실패 2분 지속.

### P1

P1은 `group_wait=30s`, `repeat_interval=1h`를 사용합니다. prod와 cluster-global P1은 Discord로 전달하고 dev P1은 muted receiver로 분리합니다.

- `PrometheusUnavailable`: 단일 Prometheus replica가 ready 상태가 아니거나 readiness metric이 없는 상태 1분 지속.
- `ApiLatencyHigh`: p95 latency 2초 초과 5분 지속.
- `JudgeWaitingQueueBacklog`: `waiting_queue` 5 초과 3분 지속.
- `CeleryWorkerRestarting`: worker restart 3회 이상/15분.
- `CeleryBeatDown`: beat Pod not ready 2분 지속.
- `PodCrashLooping`: 주요 Pod restart 증가 5분 지속.
- `PVCAlmostFull`: PVC 사용률 85% 초과 10분 지속.
- `CodePlaceCollectorFailed`: backend custom metric collector 실패 5분 지속.
- `PostgresCollectorUnavailable`: CNPG collector 응답 실패 5분 지속.
- `OpenTelemetryCollectorUnavailable`: collector target 실패 5분 지속.
- `TempoUnavailable`: Tempo target 실패 5분 지속.
- `OpenTelemetrySpanExportFailures`: Tempo span 전송 실패 5분 지속.

공개 endpoint의 실제 HTTP 실패와 synthetic probe metric 결측은 같은 장애로 취급하지 않습니다. `PublicEndpointDown`은 `probe_success == 0`만 감지하고, 수집 경로 결측은 `PublicEndpointProbeMissing` P1으로 별도 통지합니다. Alertmanager는 service별로 알림을 묶고 본문에 service와 instance를 표시합니다. 반복 전송은 신규 장애로 오인되지 않도록 `활성` 상태로 표기합니다.

Frontend runtime exception은 Kubernetes 로그가 아니라 Sentry release와 source map을 기준으로 확인합니다. 브라우저 오류를 backend Loki 로그로 가장하는 별도 panel이나 Prometheus alert은 두지 않습니다.

## 5. 운영 확인 절차

1. dev/prod 애플리케이션 delivery가 완료되어 새 backend custom metrics/trace 코드와 hub-auth `/healthz` endpoint를 포함한 image tag가 각 overlay에 반영됐는지 확인합니다. monitoring probe를 application image보다 먼저 배포하지 않습니다.
2. `alertmanager-contact-points` Secret을 운영 클러스터의 `monitoring` namespace에 생성합니다. 이 값은 Kubernetes Secret으로 참조되며, Pod 파일로 mount하지 않습니다.
3. `kubernetes/monitoring/logs/README.md`의 고정 chart version과 values로 kube-prometheus-stack, Loki, Alloy를 설치 또는 upgrade한 뒤 CodePlace monitoring resource를 적용합니다.

   ```sh
   kubectl apply -k kubernetes/monitoring
   ```

4. Traefik PodMonitor가 생성된 것을 확인한 뒤 `kubectl apply`가 정리하지 못하는 기존 ServiceMonitor를 한 번만 삭제합니다.

   ```sh
   kubectl -n monitoring get podmonitor traefik
   kubectl -n monitoring delete servicemonitor traefik --ignore-not-found
   ```

5. Prometheus를 port-forward하고 독립 live verifier로 필수 scrape/probe/custom collector/HA 계약을 확인합니다.

   ```sh
   # terminal 1
   kubectl -n monitoring port-forward service/kube-prometheus-stack-prometheus 19090:9090

   # terminal 2
   python3 kubernetes/monitoring/verify_live.py --prometheus-url http://127.0.0.1:19090
   ```

6. Grafana에서 11개 CodePlace dashboard가 provision됐는지 확인합니다. 환경별 dashboard는 `prod`와 `dev`를 각각 선택해 확인하고, `CodePlace AI Runtime (Prod)`와 `CodePlace Log Pipeline`에는 환경 selector가 없는지 확인합니다.
7. `CodePlace Logs` dashboard 또는 Explore에서 `{namespace="code-place-dev"}`와 `{namespace="code-place-prod"}`가 각각 로그를 반환하고, `CodePlace Log Pipeline`에서 Loki/Alloy 전역 상태가 조회되는지 확인합니다.
8. `CodePlace Traces`에서 dev/prod를 각각 선택해 `deployment.environment`가 분리되는지 확인합니다.
9. test alert 또는 임시 rule로 P0 webhook 수신 시간이 1분 이내인지 확인합니다.

운영 적용 전제는 다음과 같습니다.

- `/metrics`는 cluster 내부 scrape 전용이며 외부 Ingress에 노출하지 않습니다.
- Discord webhook URL은 Git에 저장하지 않습니다.
- Docker Swarm monitoring 구성은 레거시로 유지하고 신규 관측성 리소스와 분리합니다.
- OpenTelemetry는 base의 비활성 기본값 위에서 dev/prod overlay가 명시적으로 활성화합니다. service name과 deployment environment label을 제거하거나 두 환경을 같은 값으로 설정하지 않습니다.
- P0/P1 알림 라우팅은 AlertmanagerConfig로 관리하며 Grafana UI 수동 설정에 의존하지 않습니다.

## 6. 검증

로컬 검증 항목은 다음과 같습니다.

- Python compile: `python3 -m compileall backend/account backend/judge backend/oj backend/utils`
- Django check: `/tmp/code-place-backend-venv/bin/python manage.py check --settings=oj.settings`
- Metrics endpoint: Django test client 기준 `/metrics` 200 및 `codeplace_*` metric 포함 확인
- Kubernetes app render: `kubectl kustomize kubernetes/overlays/dev`, `kubectl kustomize kubernetes/overlays/prod`
- Kubernetes monitoring render: `kubectl kustomize kubernetes/monitoring`
- Dashboard environment/grid/visualization/navigation contract: `python3 kubernetes/monitoring/validate_dashboards.py --prometheus-rules-output /tmp/codeplace-dashboard-rules.json`로 11개 dashboard 검증
- Prometheus rule/PromQL parse: `promtool check rules`로 `prometheus-rules.yaml`과 validator가 추출한 dashboard PromQL 검증
- Monitoring alert contract: `validate_alerts.py`와 `promtool test rules`로 실제 장애/metric 결측 분리, 고정 replica target 일부 누락, prod/dev 지속 시간, service/instance 및 workload 문맥 전달을 검증
- Pinned Helm chart render: kube-prometheus-stack `86.3.1`, Loki `6.55.0`, Alloy `1.10.0`
- Live collection contract: Prometheus port-forward 후 `python3 kubernetes/monitoring/verify_live.py`

위 정적 계약은 `.github/workflows/monitoring-validate.yml`에서도 실행합니다. 운영 cluster의 최종 판정은 독립 실행한 `verify_live.py` 결과이며, render나 dashboard JSON parse 성공만으로 수집 성공을 대신하지 않습니다.

### Discord Webhook Secret

Discord webhook URL은 repo에 커밋하지 않습니다. SealedSecrets controller가 설치된 클러스터에서 생성합니다.

```sh
kubectl -n monitoring create secret generic alertmanager-contact-points \
  --from-literal=webhook-url="$ALERT_WEBHOOK_URL" \
  --dry-run=client -o yaml \
  | kubeseal --controller-namespace kube-system --format yaml \
  > kubernetes/monitoring/secrets/alertmanager-contact-points.sealedsecret.yaml
```
