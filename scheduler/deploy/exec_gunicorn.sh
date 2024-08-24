#!/bin/sh

# 환경 변수가 설정되지 않았다면 기본값 사용
LOG_PATH=${LOG_PATH:-/app/logs/gunicorn.log}

# 로그 디렉토리가 존재하는지 확인하고 없다면 생성
mkdir -p $(dirname $LOG_PATH)

exec gunicorn csep_scheduler.wsgi \
    --bind 127.0.0.1:8090 \
    --workers 1 \
    --log-file "$LOG_PATH" \
    --capture-output