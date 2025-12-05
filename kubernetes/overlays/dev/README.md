# Development (`dev`) 환경 PostgreSQL Credentials

이 디렉토리는 `dev` 환경을 위한 PostgreSQL `pg-credentials` Secret을 `SealedSecret`으로 정의합니다.

## 주요 파일

- `pg-credentials.yaml`: `dev` 환경의 PostgreSQL `username`과 `password`를 포함하는 `SealedSecret` 리소스입니다.
- `kustomization.yaml`: 이 `overlay`의 설정을 정의하며, `pg-credentials.yaml`을 리소스로 포함합니다.

## 사전 조건 (Prerequisites)

`SealedSecret`을 생성하거나 관리하기 전에, `Sealed Secrets Controller`와 `kubeseal` CLI가 설치되어 있어야 합니다. 설치 방법은 [Kubernetes 구성 가이드](../../README.md)를 참고하세요.

## 현재 설정

`dev` 환경의 PostgreSQL `username`과 `password`는 `pg-credentials.yaml` 파일에 `SealedSecret`으로 암호화되어 저장되어 있습니다. Kustomize가 `overlay`를 빌드할 때 이 파일을 함께 적용하여 `pg-credentials` Secret을 생성합니다.

## Credential 재생성

만약 `dev` 환경의 credential을 변경해야 한다면, 다음 절차에 따라 `pg-credentials.yaml` 파일을 재생성할 수 있습니다.

1.  **Secret 생성 및 암호화:**
    `username`과 `password`를 새로 설정하여 명령어를 실행합니다. 네임스페이스는 `code-place-dev` 입니다.

    ```sh
    kubectl create secret generic pg-credentials \
      --from-literal=username=<NEW_USERNAME> \
      --from-literal=password=<NEW_PASSWORD> \
      --namespace=code-place-dev \
      --dry-run=client -o yaml | \
    kubeseal \
      --controller-name=sealed-secrets-controller \
      --controller-namespace=kube-system \
      --format=yaml > pg-credentials.yaml
    ```

2.  **변경사항 커밋:**
    새로 생성된 `pg-credentials.yaml` 파일을 Git에 커밋합니다.
