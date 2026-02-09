# Grafana (Helm) 배포 가이드

이 디렉토리는 Grafana Helm Chart의 설정을 환경별로 관리합니다.

-   `base/monitoring/grafana/values.yaml`: 모든 환경에 적용되는 공통 설정 파일입니다.
-   `overlays/<환경>/grafana-values.yaml`: 각 환경에만 적용되는 특별 설정 파일입니다. (예: Ingress 호스트 주소)

## 사전 조건

-   `helm` CLI가 설치되어 있어야 합니다.
-   `kubectl`이 클러스터에 연결되어 있어야 합니다.
-   Grafana Helm 리포지토리가 추가되어 있어야 합니다.

```sh
# 리포지토리 추가 (최초 1회)
helm repo add grafana https://grafana-community.github.io/helm-charts
helm repo update
```

## 환경별 배포 명령어

`helm upgrade --install` 명령어를 사용하여 Grafana를 설치하거나 업그레이드합니다.
`-f` 옵션을 사용하여 **공통 `values.yaml`을 먼저 지정하고, 그 다음 환경별 `values.yaml`을 지정**하여 설정을 덮어씁니다.

### Dev 환경 배포

```sh
# 프로젝트 루트 디렉토리에서 실행

helm upgrade --install grafana grafana/grafana \
  --namespace monitoring \
  --create-namespace \
  -f kubernetes/base/monitoring/grafana/values.yaml \
  -f kubernetes/overlays/dev/grafana-values.yaml
```

### Prod 환경 배포

```sh
# 프로젝트 루트 디렉토리에서 실행

helm upgrade --install grafana grafana/grafana \
  --namespace monitoring \
  --create-namespace \
  -f kubernetes/base/monitoring/grafana/values.yaml \
  -f kubernetes/overlays/prod/grafana-values.yaml
```

