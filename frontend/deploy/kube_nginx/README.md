# K3s 배포용 Nginx 설정

이 디렉토리는 K3s (Kubernetes) 환경에 배포하기 위해 특별히 구성된 Nginx 설정 파일을 포함합니다.

### 기존 Nginx 설정과의 차이점

K3s로 마이그레이션한 후, TLS (Transport Layer Security) 종료에 대한 책임은 상위의 Traefik이 담당합니다.
따라서 이 Nginx 인스턴스는 더 이상 TLS 인증 및 종료를 수행하지 않습니다.
대신, Traefik이 모든 인바운드 TLS 트래픽을 처리한 후 암호화되지 않은 HTTP 트래픽을 이 Nginx 서비스로 프록시합니다.

참고로, TLS 처리를 포함했던 이전 Nginx 설정은 `frontend/deploy/nginx/` 디렉토리에서 확인할 수 있습니다.
