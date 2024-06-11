#!/bin/sh

APP=/app # 앱 데이터 경로 설정
DATA=/data # 데이터 디렉토리 경로 설정

# log, config, ssl, test_case, avatar 디렉토리 생성
mkdir -p $DATA/log $DATA/config $DATA/ssl $DATA/test_case $DATA/public/upload $DATA/public/avatar $DATA/public/website

#secret key가 존재하지 않는 경우 생성
if [ ! -f "$DATA/config/secret.key" ]; then
    echo $(cat /dev/urandom | head -1 | md5sum | head -c 32) > "$DATA/config/secret.key"
fi

# avatar default 이미지가 존재하지 않는 경우 기존 디렉토리에서 복사 및 생성
if [ ! -f "$DATA/public/avatar/default.png" ]; then
    cp data/public/avatar/default.png $DATA/public/avatar
fi

# favicon이 없으면 기존 디렉토리에서 복사 및 생성
if [ ! -f "$DATA/public/website/favicon.ico" ]; then
    cp data/public/website/favicon.ico $DATA/public/website
fi

# SSL 인증서 및 키가 없다면, 생성
SSL="$DATA/ssl"
if [ ! -f "$SSL/server.key" ]; then
    openssl req -x509 -newkey rsa:2048 -keyout "$SSL/server.key" -out "$SSL/server.crt" -days 1000 \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=Beijing OnlineJudge Technology Co., Ltd./OU=Service Infrastructure Department/CN=`hostname`" -nodes
fi

# Nginx 구성파일의 심볼릭 링크 생성, Https 강제 설정 여부에 따라 다름. default는 false
cd $APP/deploy/nginx
ln -sf locations.conf https_locations.conf
if [ -z "$FORCE_HTTPS" ]; then
    ln -sf locations.conf http_locations.conf
else
    ln -sf https_redirect.conf http_locations.conf
fi

# API 프록시 구성 파일에서 IP 헤더 설정
if [ ! -z "$LOWER_IP_HEADER" ]; then
    sed -i "s/__IP_HEADER__/\$http_$LOWER_IP_HEADER/g" api_proxy.conf;
else
    sed -i "s/__IP_HEADER__/\$remote_addr/g" api_proxy.conf;
fi

# CPU 코어 수에따른 최대 워커 프로세스 수 조정
if [ -z "$MAX_WORKER_NUM" ]; then
    export CPU_CORE_NUM=$(grep -c ^processor /proc/cpuinfo)
    if [[ $CPU_CORE_NUM -lt 2 ]]; then
        export MAX_WORKER_NUM=2
    else
        export MAX_WORKER_NUM=$(($CPU_CORE_NUM))
    fi
fi

# static contents 전송을 위한 CDN 호스트 설정
cd $APP/dist
if [ ! -z "$STATIC_CDN_HOST" ]; then
    find . -name "*.*" -type f -exec sed -i "s/__STATIC_CDN_HOST__/\/$STATIC_CDN_HOST/g" {} \;
else
    find . -name "*.*" -type f -exec sed -i "s/__STATIC_CDN_HOST__\///g" {} \;
fi

cd $APP

n=0
while [ $n -lt 5 ]
do
    python3 manage.py migrate contest 0011
    python3 manage.py migrate --no-input
    python manage.py inituser --username=root --password=rootroot --action=create_super_admin &&
    echo "from options.options import SysOptions; SysOptions.judge_server_token='$JUDGE_SERVER_TOKEN'" | python manage.py shell &&
    echo "from conf.models import JudgeServer; JudgeServer.objects.update(task_number=0)" | python manage.py shell &&
    break
    n=$(($n+1))
    echo "Failed to migrate, going to retry..."
    sleep 8
done

echo "Loading Fixtures..."
sleep 2
python3 manage.py loaddata $APP/fixtures/*.json
echo "Fixtures loaded!"

addgroup -g 903 spj
adduser -u 900 -S -G spj server

chown -R server:spj $DATA $APP/dist
find $DATA/test_case -type d -exec chmod 710 {} \;
find $DATA/test_case -type f -exec chmod 640 {} \;

# supervisord 프로세스 관리자를 실행
exec supervisord -c /app/deploy/supervisord.conf
