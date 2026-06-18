# Grafana (Helm) 배포 가이드

이 디렉토리는 `monitoring` namespace에 배포되는 shared Grafana Helm Chart 설정을 관리합니다.

-   `monitoring/grafana/values.yaml`: 공통 설정 파일입니다.
-   `monitoring/grafana/values-ingress.yaml`: `monitoring.code-place-dev.site` reverse proxy 설정 파일입니다.

## 사전 조건

-   `helm` CLI가 설치되어 있어야 합니다.
-   `kubectl`이 클러스터에 연결되어 있어야 합니다.
-   Grafana Helm 리포지토리가 추가되어 있어야 합니다.

```sh
# 리포지토리 추가 (최초 1회)
helm repo add grafana https://grafana-community.github.io/helm-charts
helm repo update
```

## 배포 명령어

`helm upgrade --install` 명령어를 사용하여 Grafana를 설치하거나 업그레이드합니다.
`-f` 옵션을 사용하여 **공통 `values.yaml`을 먼저 지정하고, 그 다음 ingress `values-ingress.yaml`을 지정**하여 설정을 덮어씁니다.

```sh
# 프로젝트 루트 디렉토리에서 실행

helm upgrade --install grafana grafana/grafana \
  --namespace monitoring \
  --create-namespace \
  -f kubernetes/monitoring/grafana/values.yaml \
  -f kubernetes/monitoring/grafana/values-ingress.yaml
```

현재 Grafana 외부 도메인은 `monitoring.code-place-dev.site` 하나입니다. subdomain reverse proxy 방식이라 별도 `root_url`/subpath 설정은 사용하지 않습니다.
