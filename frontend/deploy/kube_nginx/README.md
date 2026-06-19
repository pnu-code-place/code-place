# K3s 배포용 Nginx 설정

이 디렉토리는 K3s (Kubernetes) 환경에 배포하기 위해 특별히 구성된 Nginx 설정 파일을 포함합니다.

### 기존 Nginx 설정과의 차이점

K3s로 마이그레이션한 후, TLS (Transport Layer Security) 종료에 대한 책임은 상위의 Traefik이 담당합니다.
따라서 이 Nginx 인스턴스는 더 이상 TLS 인증 및 종료를 수행하지 않습니다.
대신, Traefik이 모든 인바운드 TLS 트래픽을 처리한 후 암호화되지 않은 HTTP 트래픽을 이 Nginx 서비스로 프록시합니다.

### 관측성

Kubernetes용 Nginx는 access log를 JSON 형식으로 `/dev/stdout`에 출력하고 error log를 `/dev/stderr`에 출력합니다.
들어온 `X-Request-ID`가 있으면 그대로 유지하고, 없으면 Nginx `$request_id`를 생성해 응답 header와 backend proxy header로 전달합니다.
이 값은 frontend nginx log, backend JSON log, Celery task log를 Loki에서 같은 `request_id`로 조회하는 데 사용합니다.

참고로, TLS 처리를 포함했던 이전 Nginx 설정은 `frontend/deploy/nginx/` 디렉토리에서 확인할 수 있습니다.
