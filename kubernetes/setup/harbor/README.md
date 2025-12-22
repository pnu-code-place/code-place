# Harbor 설치 가이드

이 문서는 Helm과 제공된 `values.yaml` 템플릿 파일을 사용하여 Kubernetes 클러스터에 Harbor를 설치하는 방법을 안내합니다.

### 핵심 파일

- `values.yaml`: Harbor Helm 차트의 핵심 설정을 정의하는 템플릿 파일입니다.
  - 이 파일에는 `##HARBOR_HOST##`나 `##HARBOR_ADMIN_PASSWORD##`와 같은 플레이스홀더가 포함되어 있습니다.
  - 실제 배포 시 이 파일을 복사하여 플레이스홀더들을 실제 값으로 교체해야 합니다.
  - **참고로 `expose.tls.certSource: none`은 Ingress(Traefik)가 TLS 인증서 관리를 담당함을 의미합니다.**

---

### 1. 설정 파일 및 환경 변수 준비

Harbor를 설치하기 위해 설정 파일을 복사하고, 필요한 값들을 환경 변수로 지정합니다.

#### 1-1. 설정 파일 복사

원본 `values.yaml` 템플릿을 `my-values.yaml`이라는 이름으로 복사하여 실제 설정 파일로 사용합니다. 이렇게 하면 원본 템플릿을 유지할 수 있습니다.

```sh
cp ./values.yaml ./my-values.yaml
```

#### 1-2. 환경 변수 설정

Harbor에 사용할 호스트 이름과 관리자 계정의 초기 비밀번호를 환경 변수로 지정합니다.

```sh
export HARBOR_HOST="harbor.your-domain.com"      # Harbor에 접근할 전체 주소 (FQDN)
export HARBOR_ADMIN_PASSWORD="YourSecurePassword"      # Harbor admin 계정의 비밀번호
```

---

### 2. 설정 값 변경 및 설치

`sed` 명령어를 사용하여 `my-values.yaml` 파일의 플레이스홀더 값을 위에서 설정한 환경 변수 값으로 교체한 후, Helm을 이용해 Harbor를 설치합니다.

#### 2-1. 설정 파일 내용 변경

`sed`를 사용하여 `values.yaml`에 정의된 플레이스홀더를 환경 변수 값으로 자동으로 변경합니다.

```sh
# 1. Harbor 호스트 주소 변경 (my-values.yaml 내 ##HARBOR_HOST## 플레이스홀더를 변경)
sed -i.bak "s/##HARBOR_HOST##/$HARBOR_HOST/g" ./my-values.yaml

# 2. Harbor 관리자 비밀번호 변경 (my-values.yaml 내 ##HARBOR_ADMIN_PASSWORD## 플레이스홀더를 변경)
sed -i.bak "s/##HARBOR_ADMIN_PASSWORD##/$HARBOR_ADMIN_PASSWORD/g" ./my-values.yaml
```
> **참고:** `sed -i` 명령어는 macOS와 GNU/Linux에서 다르게 동작할 수 있습니다. 호환성을 위해 `.bak` 확장자를 사용했습니다. macOS에서는 `sed -i '' "s/..."` 와 같이 사용해야 할 수 있습니다.

#### 2-2. Helm을 이용한 Harbor 설치

준비된 `my-values.yaml` 파일을 사용하여 `harbor` 네임스페이스에 Harbor를 설치합니다.

```sh
# Harbor Helm 리포지토리 추가 (아직 추가하지 않은 경우)
helm repo add harbor https://helm.goharbor.io
helm repo update

# Helm 차트 설치
helm install harbor harbor/harbor \
  --create-namespace \
  --namespace harbor \
  --values ./my-values.yaml
```

설치가 완료되면 `externalURL` 또는 `expose.ingress.hosts.core`에 설정한 주소로 Harbor UI에 접속할 수 있습니다.
