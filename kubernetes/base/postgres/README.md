# Postgres (CNPG) 배포 가이드

이 문서는 CNPG (CloudNativePG) Operator를 사용하여 PostgreSQL 클러스터를 쿠버네티스 클러스터에 배포하는 방법을 안내합니다.

### 핵심 파일

- `postgres.yaml`: CNPG Operator를 통해 PostgreSQL 클러스터를 생성하기 위한 Custom Resource(CR) 정의 파일입니다.

---

## 1. 사전 조건 (Prerequisites)

이 설정을 적용하기 전에, 클러스터에 **CNPG Operator**와 **Sealed Secrets Controller**가 반드시 설치되어 있어야 합니다.

### 1-1. CNPG Operator 설치

CloudNativePG의 공식 Helm 차트 리포지토리를 추가하고 Operator를 설치합니다.

```sh
helm repo add cnpg https://cloudnative-pg.github.io/charts

helm upgrade --install cnpg \
  --namespace cnpg-system \
  --create-namespace \
  cnpg/cloudnative-pg
```

### 1-2. Sealed Secrets Controller 설치

Bitnami Labs의 Sealed Secrets 컨트롤러를 설치합니다. 이 컨트롤러는 클러스터 내에서 암호화된 Secret을 안전하게 복호화하는 역할을 합니다. `kubeseal` CLI 설치도 필요합니다.

```sh
# Helm Chart 설치
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm install sealed-secrets -n kube-system --set-string fullnameOverride=sealed-secrets-controller sealed-secrets/sealed-secrets

# kubeseal CLI 설치 (Linux amd64 예시)
KUBESEAL_VERSION=0.33.0
curl -OL "https://github.com/bitnami-labs/sealed-secrets/releases/download/v${KUBESEAL_VERSION}/kubeseal-${KUBESEAL_VERSION}-linux-amd64.tar.gz"
tar -xvzf kubeseal-${KUBESEAL_VERSION}-linux-amd64.tar.gz kubeseal
sudo install -m 755 kubeseal /usr/local/bin/kubeseal
```

### 1-3. PostgreSQL Credentials Secret 생성

PostgreSQL 클러스터는 초기 데이터베이스와 소유자(owner)를 설정하기 위해 `username`과 `password`가 포함된 Secret을 필요로 합니다. `base` 설정에서는 `pg-credentials`라는 이름의 Secret을 참조합니다.

이 Secret은 각 `overlay` 환경(`dev`, `prod`, `stage` 등)에서 **SealedSecret**을 사용하여 생성해야 합니다. 각 `overlay` 디렉토리 환경에 맞는 `SealedSecret`을 생성하고 적용하세요.

---

## 2. 배포 (Deployment)

사전 조건이 모두 충족되었다면, `kustomize`를 사용하여 `overlay` 설정을 빌드하고 클러스터에 적용합니다. 그러면 `base`의 `postgres.yaml`이 각 환경에 맞게 수정되어 배포됩니다.

예를 들어, `dev` 환경에 배포하려면 프로젝트 루트에서 다음 명령을 실행합니다:

```sh
kustomize build kubernetes/overlays/dev | kubectl apply -f -
```

> **관련 문서:** 더 자세한 정보는 [CloudNativePG 공식 문서](https://cloudnative-pg.io/documentation/current/)를 참고하세요.
