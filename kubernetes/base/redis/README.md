# Redis (Standalone) 배포 가이드

이 문서는 Redis Operator를 사용하여 Standalone 모드의 Redis 인스턴스를 쿠버네티스 클러스터에 배포하는 방법을 안내합니다.

### 핵심 파일

- `redis.yaml`: Redis Operator를 통해 Redis Standalone 인스턴스를 생성하기 위한 Custom Resource(CR) 정의 파일입니다.

---

## 1. 사전 조건 (Prerequisites)

이 설정을 적용하기 전에, 클러스터에 **Redis Operator**가 반드시 설치되어 있어야 합니다.

#### 1-1. Helm 리포지토리 추가

Opstree Redis Operator의 공식 Helm 차트 리포지토리를 추가합니다.

```sh
helm repo add ot-helm https://ot-container-kit.github.io/helm-charts/
helm repo update
```

#### 1-2. Redis Operator 설치

다음 명령어를 사용하여 클러스터에 Redis Operator를 설치합니다.

```sh
helm install redis-operator ot-helm/redis-operator
```

설치가 완료되면, Redis Custom Resource를 관리할 준비가 된 것입니다.

---

## 2. 배포 (Deployment)

사전 조건이 충족되었다면, `redis.yaml` 파일을 클러스터에 적용하여 Redis 인스턴스를 배포할 수 있습니다. `redis.yaml` 파일은 현재 `kubernetes/base/redis/` 디렉토리에 있습니다.

```sh
kubectl apply -f ../backend/redis.yaml
```

> **관련 문서:** 더 자세한 정보는 [Redis Operator 공식 문서](https://redis-operator.opstree.dev/docs/getting-started/standalone/)를 참고하세요.

---

## 3. 향후 개선 사항 (TODO)

- 현재 구성은 단일 파드로 운영되는 **Standalone 모드**입니다.
- 향후 서비스 트래픽이 증가하거나 더 높은 수준의 가용성이 요구될 경우, **Sentinel 또는 Cluster 모드**로 전환하는 것을 검토해야 합니다. (Junwoo)
