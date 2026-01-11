---
date: "2026-01-10T19:03:32+09:00"
draft: false
title: "Traefik TLS 설정"
---

{{< callout >}}
이 문서에서는 Traefik이 TLS 인증서 발급을 담당하도록 하는 방법과, 새로운 Ingress에 TLS 인증을 추가하는 방법에 대해 설명합니다.
{{< /callout >}}

웹페이지에서 HTTP가 아닌 HTTPS로 접근하기 위해서는 주기적인 TLS 인증서 발급이 필수입니다.

코드플레이스는 **Traefik**에 내장되어 있는 `Let's Encrypt`를 통해 인증서를 발급받고 있습니다.
그 이유는 크게 다음과 같습니다.

- Ingress를 구성할 때 단 몇 줄의 코드로 TLS 인증서를 발급받을 수 있습니다.
- Traefik이 인증서 만료일을 추적하고, 30일 이내인 인증서를 자동으로 갱신해줍니다.

## Traefik 인증서 발급 설정

K3s 클러스터에 설치된 Traefik의 Let's Encrypt 연동 설정은 `kubernetes/setup/traefik/traefik-config.yaml` 파일에서 관리됩니다. 이 파일은 K3s가 기본으로 설치하는 Traefik Helm Chart의 설정을 덮어씁니다.

```yaml
# kubernetes/setup/traefik/traefik-config.yaml
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    additionalArguments:
      - "--certificatesresolvers.default.acme.email=<EMAIL_ADDRESS>"
      - "--certificatesresolvers.default.acme.storage=/data/acme.json"
      - "--certificatesresolvers.default.acme.tlschallenge=true" # 443 포트를 통해 인증

    # ... (중략) ...

    persistence:
      enabled: true
      name: data
      accessMode: ReadWriteMany # 여러 노드에서 읽기/쓰기가 가능하도록 설정
      size: 128Mi
      storageClass: "longhorn"
      path: /data

    deployment:
      initContainers:
        - name: volume-permissions
          image: busybox:latest
          command:
            - "sh"
            - "-c"
            - |
              touch /data/acme.json
              chmod 600 /data/acme.json
              chown 65532:65532 /data/acme.json
          volumeMounts:
            - name: data
              mountPath: /data
      podSecurityContext:
        fsGroup: 65532
```

### 주요 설정 항목

- `additionalArguments`: Traefik의 동작을 설정하는 핵심 인자입니다.
  - `--certificatesresolvers.default.acme.email`: Let's Encrypt 계정으로 사용할 이메일 주소입니다. 인증서 만료 알림 등을 받을 때 사용됩니다.
  - `--certificatesresolvers.default.acme.storage`: 발급된 TLS 인증서와 개인키가 저장될 경로입니다. `acme.json` 파일에 모든 정보가 기록됩니다.
  - `--certificatesresolvers.default.acme.tlschallenge=true`: 도메인 소유권을 증명하는 ACME Challenge 방식으로 **TLS-AL-01**을 사용하도록 설정합니다. 이 방식은 443 포트를 통해 이루어지므로, 웹 트래픽과 동일한 포트를 사용하여 방화벽 관리가 용이합니다.
- `persistence`: `acme.json` 파일을 영구적으로 보관하기 위한 설정입니다.
  - Traefik 파드가 재시작되더라도 인증서 정보가 유실되지 않도록 `PersistentVolumeClaim`을 사용합니다.
  - 코드플레이스에서는 `longhorn` 스토리지 클래스를 통해 PVC를 생성합니다.
- `deployment.initContainers`: `acme.json` 파일의 권한 문제를 해결하기 위한 설정입니다.
  - Traefik은 보안상의 이유로 `non-root` 유저(UID 65532)로 실행됩니다.
  - `initContainer`는 메인 컨테이너가 시작되기 전에 실행되어 `acme.json` 파일이 존재하도록 보장하고, 파일 권한을 `600`으로, 소유자를 `65532`로 설정하여 Traefik 프로세스가 안전하게 파일에 접근할 수 있도록 합니다.

## Ingress에 TLS 인증서 추가하기

Traefik 설정이 완료되었다면, Ingress 리소스에 몇 가지 `annotation`과 `tls` 설정을 추가하는 것만으로 간단하게 HTTPS를 적용할 수 있습니다.

다음은 `frontend-ingress`에 `prod` 환경의 도메인(`code.pusan.ac.kr`)을 위한 TLS 인증서를 적용하는 예시입니다.

1.  **기본 Ingress 정의 (`kubernetes/base/frontend/ingress.yaml`)**

    ```yaml
    # kubernetes/base/frontend/ingress.yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: frontend-ingress
      annotations:
        # 이 Ingress를 Traefik이 관리하도록 지정
        kubernetes.io/ingress.class: traefik
        # 'default'라는 이름의 Certificate Resolver를 사용해 TLS 인증서를 발급
        traefik.ingress.kubernetes.io/router.tls.certresolver: default
    # NOTE: 호스트 및 경로 설정은 패치 파일에서 관리됩니다.
    ```

2.  **환경별 Ingress 패치 (`kubernetes/overlays/prod/frontend-ingress-patch.yaml`)**

    ```yaml
    # kubernetes/overlays/prod/frontend-ingress-patch.yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: frontend-ingress
    spec:
      rules:
        # 어떤 호스트 이름으로 요청이 들어올 때 적용할지 정의
        - host: code.pusan.ac.kr
          http:
            paths:
              - path: /
                pathType: Prefix
                backend:
                  service:
                    name: frontend
                    port:
                      number: 80
      # TLS를 적용할 호스트 목록을 명시
      tls:
        - hosts:
            - code.pusan.ac.kr
    ```

### 설정 단계 요약

새로운 서비스에 TLS 인증서를 발급하려면 다음과 같이 Ingress 리소스를 작성하면 됩니다.

1.  `metadata.annotations`에 `traefik.ingress.kubernetes.io/router.tls.certresolver: default`를 추가하여 Let's Encrypt 자동 발급 기능을 활성화합니다.
2.  `spec.rules`에 TLS를 적용할 `host`를 정의합니다.
3.  `spec.tls` 블록에 `host`와 동일한 도메인 이름을 추가합니다.

이렇게 설정된 Ingress가 클러스터에 배포되면, Traefik은 `tls` 블록에 명시된 `host`를 감지하고, `certresolver` 설정을 따라 Let's Encrypt에 해당 도메인의 TLS 인증서를 요청합니다. 발급이 완료되면 자동으로 해당 인증서를 적용하여 HTTPS 트래픽을 처리합니다.
