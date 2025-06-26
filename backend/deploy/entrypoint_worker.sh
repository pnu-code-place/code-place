#!/bin/sh

APP=/app # 앱 데이터 경로 설정
DATA=/data # 데이터 디렉토리 경로 설정

# log, config, test_case, avatar, banner, popup 디렉토리 생성
mkdir -p $DATA/log $DATA/config $DATA/test_case $DATA/public/upload $DATA/public/avatar $DATA/public/website $DATA/public/banner $DATA/public/popup

if [ ! -f "$DATA/config/secret.key" ]; then
    echo `cat /dev/urandom | head -1 | md5sum | head -c 32` > $DATA/config/secret.key
fi

# CPU 코어 수에 따른 최대 워커 프로세스 수 조정
if [ -z "$MAX_WORKER_NUM" ]; then
    export CPU_CORE_NUM=$(grep -c ^processor /proc/cpuinfo)
    if [[ $CPU_CORE_NUM -lt 2 ]]; then
        export MAX_WORKER_NUM=2
    else
        export MAX_WORKER_NUM=$(($CPU_CORE_NUM))
    fi
fi

cd $APP

addgroup -g 903 celeryworker
adduser -u 900 -S -G celeryworker celeryworker

chown -R celeryworker:celeryworker $DATA

exec supervisord -c /app/deploy/supervisord.worker.conf
