#!/bin/sh

APP=/app # 앱 데이터 경로 설정
DATA=/data # 데이터 디렉토리 경로 설정

DEFAULT_WORKER_NUM=4 # 기본 워커 프로세스 수 설정

# log, config, test_case, avatar, banner, popup 디렉토리 생성
mkdir -p $DATA/log $DATA/config $DATA/test_case $DATA/public/upload $DATA/public/avatar $DATA/public/website $DATA/public/banner $DATA/public/popup

if [ ! -f "$DATA/config/secret.key" ]; then
    echo `cat /dev/urandom | head -1 | md5sum | head -c 32` > $DATA/config/secret.key
fi

# MAX_WORKER_NUM 환경 변수가 설정되지 않은 경우 기본값 사용
if [ -z "$MAX_WORKER_NUM" ]; then
    export MAX_WORKER_NUM=$DEFAULT_WORKER_NUM
fi

cd $APP

addgroup -g 903 celeryworker
adduser -u 900 -S -G celeryworker celeryworker

chown -R celeryworker:celeryworker $DATA

exec supervisord -c /app/deploy/supervisord.worker.conf
