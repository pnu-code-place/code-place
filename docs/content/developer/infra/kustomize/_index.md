---
date: "2026-01-11T14:32:07+09:00"
draft: false
title: "Kustomize 기반 리소스 정의 및 릴리즈"
weight: 2
---

{{< callout >}}
이 문서에서는 Kustomize의 기본 개념과 코드플레이스 내에서의 활용 방법에 대해 설명합니다. 코드플레이스를 각 환경에 맞게 릴리즈하고 관리하는 방법도 포함되어 있습니다.
{{< /callout >}}

**Kustomize**는 쿠버네티스 리소스의 선언적 관리를 위한 도구로, YAML 파일을 조작하고 구성하는 데 사용됩니다. 코드플레이스에서는 Kustomize를 사용하여 각 환경(개발, 프로덕션 등)에 맞게 쿠버네티스 리소스를 커스터마이징하고 있습니다.

## Kustomize 기본 개념

Kustomize를 이해하기 위해서는 `base`와 `overlay` 개념을 알아야 합니다.

- **Base**: 모든 환경에서 공통적으로 사용되는 리소스의 원본 정의를 포함하는 디렉토리입니다. 예를 들어, 애플리케이션의 기본 배포(Deployment)나 서비스(Service) 설정이 여기에 포함됩니다.
- **Overlay**: 특정 환경에 맞게 `base`의 설정을 덮어쓰거나 변경(patch)하는 디렉토리입니다. 예를 들어, 개발 환경에서는 리소스 요청을 낮게 설정하고, 프로덕션 환경에서는 더 높은 설정을 적용하는 등의 차이를 관리합니다.

정리하면, `base`에서 환경에 독립적인 리소스를 정의하고, `overlay`에서 환경별로 필요한 변경 사항을 적용하는 방식입니다.

## Kustomize의 동작 원리: Base와 Overlay

Kustomize는 `kustomization.yaml` 파일 하나로 `base`와 `overlay`를 연결합니다.
이 파일은 `base`의 공통 리소스를 가져와 `overlay`의 차이점을 덧씌우는(patch) 역할을 합니다.

코드플레이스의 `prod` 환경 `kustomization.yaml`을 예시로 이 과정을 단계별로 설명하겠습니다.

```yaml
# kubernetes/overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
  - ./secrets/pg-credentials.yaml
  - ./secrets/regcred.yaml
  - ./secrets/common-credentials.yaml

namespace: code-place-prod

patches:
  - path: backend-deployment-patch.yaml
  - path: frontend-deployment-patch.yaml
  # ... 등등
```

### 1. 리소스 취합 (`resources`)

Kustomize는 빌드를 시작할 때 `resources` 필드에 정의된 모든 YAML 파일을 불러옵니다.

- `../../base`: 모든 환경의 기반이 되는 공통 base 리소스(Deployment, Service 등)를 모두 가져옵니다.
- `./secrets/*.yaml`: `prod` 환경에만 필요한 추가 리소스, 즉 환경별 인증 정보(SealedSecret)를 가져옵니다.

이 과정을 거치면, Kustomize는 `base`와 `overlay`의 모든 리소스를 하나의 큰 집합으로 취합합니다.

### 2. 패치 적용 및 수정 (`patches`)

이 단계가 Kustomize 커스터마이징의 핵심입니다. `patches`에 정의된 파일들은 `base` 리소스를 어떻게 수정할지 명시합니다.

Kustomize는 **Strategic Merge Patch** 방식을 사용하여 `base` 리소스 위에 `patch` 파일의 내용을 덮어씁니다.
이름(`metadata.name`)을 기준으로 원본 리소스를 찾아 변경할 필드만 정확히 수정합니다.

#### 예시: `replicas` 수 변경

`base`의 `backend-deployment.yaml`은 기본적으로 `replicas`를 2로 설정합니다.

```yaml
# kubernetes/base/backend/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
    replicas: 2
  ...
```

`prod` 환경에서는 더 많은 트래픽을 감당해야 하므로, `overlays/prod`의 `backend-deployment-patch.yaml`에 변경할 부분만 다음과 같이 명시합니다.

```yaml
# kubernetes/overlays/prod/backend-deployment-patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 6
```

`kustomize build` 시, Kustomize는 `base`의 `Deployment` 중 이름이 `backend`인 리소스를 찾아 `spec.replicas` 값을 `6`으로 덮어씁니다.
이미지 태그, 도메인 이름 등 다른 모든 커스터마이징도 이와 동일한 원리로 동작합니다.

### 3. 최종 매니페스트 생성

모든 `patch`와 `namespace` 적용이 끝나면, Kustomize는 모든 리소스가 조합되고 수정된 최종 매니페스트를 생성합니다.
이 결과물은 클러스터에 바로 적용할 수 있는 완전한 상태가 됩니다.

## 각 환경별 릴리즈 방법

Kustomize는 간단한 명령어로 특정 환경에 맞는 최종 쿠버네티스 매니페스트를 생성하고, 이를 `kubectl`로 클러스터에 바로 적용할 수 있게 해줍니다.

### 1. 개발(dev) 환경에 배포하기

개발 환경에 배포하려면, `kubernetes/overlays/dev` 디렉토리를 대상으로 `kubectl apply -k` 명령어를 실행합니다.
이 명령어는 `code-place-dev` 네임스페이스에 리소스를 배포합니다.

```shell
kubectl apply -k kubernetes/overlays/dev
```

### 2. 프로덕션(prod) 환경에 배포하기

개발 환경과 동일한 방식이지만, 대상 디렉토리를 `prod`로 변경하면 됩니다. 이 명령어는 `code-place-prod` 네임스페이스에 리소스를 배포합니다.

```shell
kubectl apply -k kubernetes/overlays/prod
```

{{< callout type="warning" >}}
**배포 전 최종 설정 확인**

특히 프로덕션 환경에 배포하기 전에는 어떤 변경사항이 적용될지 미리 확인하는 것이 안전합니다. `kubectl apply`를 실행하기 전에 다음 명령어로 최종 생성될 YAML 파일을 검토할 수 있습니다.

```shell
# prod 환경의 최종 YAML을 터미널에 출력하여 확인
kustomize build kubernetes/overlays/prod
```

{{< /callout >}}
