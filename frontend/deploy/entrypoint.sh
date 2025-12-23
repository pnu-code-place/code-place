#!/bin/sh

APP=/app
DIST=/usr/share/nginx/html

# Nginx 구성파일의 심볼릭 링크 생성, Https 강제 설정 여부에 따라 다름. default는 false
# K3s 환경에서 /kube_nginx 폴더 사용 (기존 /nginx 폴더는 Docker Swarm 용으로 Deprecated)
cd $APP/deploy/kube_nginx
ln -sf locations.conf https_locations.conf
if [ -z "$FORCE_HTTPS" ]; then
    ln -sf locations.conf http_locations.conf
else
    ln -sf https_redirect.conf http_locations.conf
fi

echo "Using SERVER_NAME: $SERVER_NAME"

# 동적으로 server_name 변경
sed -i "s/__SERVER_NAME__/$SERVER_NAME/g" /app/deploy/kube_nginx/nginx.conf
# sed -i "s/__SERVER_NAME__/$SERVER_NAME/g" /app/deploy/nginx/ssl_config.conf

# static contents 전송을 위한 CDN 호스트 설정
cd $DIST
if [ ! -z "$STATIC_CDN_HOST" ]; then
    find . -name "*.*" -type f -exec sed -i "s/__STATIC_CDN_HOST__/\/$STATIC_CDN_HOST/g" {} \;
else
    find . -name "*.*" -type f -exec sed -i "s/__STATIC_CDN_HOST__\///g" {} \;
fi

cd $APP

exec nginx -c /app/deploy/kube_nginx/nginx.conf
