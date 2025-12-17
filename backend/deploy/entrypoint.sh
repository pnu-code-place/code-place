#!/bin/sh

APP=/app # 앱 데이터 경로 설정
DATA=/data # 데이터 디렉토리 경로 설정

DEFAULT_WORKER_NUM=2 # 기본 워커 프로세스 수 설정

# log, config, test_case, avatar, banner, popup 디렉토리 생성
mkdir -p $DATA/log $DATA/config $DATA/test_case $DATA/public/upload $DATA/public/avatar $DATA/public/website $DATA/public/banner $DATA/public/popup

if [ ! -f "$DATA/config/secret.key" ]; then
    echo `cat /dev/urandom | head -1 | md5sum | head -c 32` > $DATA/config/secret.key
fi

# avatar default 이미지가 존재하지 않는 경우 기존 디렉토리에서 복사 및 생성
if [ ! -f "$DATA/public/avatar/default.png" ]; then
    cp data/public/avatar/default.png $DATA/public/avatar
fi

# favicon이 없으면 기존 디렉토리에서 복사 및 생성
if [ ! -f "$DATA/public/website/favicon.ico" ]; then
    cp data/public/website/favicon.ico $DATA/public/website
fi

# MAX_WORKER_NUM 환경 변수가 설정되지 않은 경우 기본값 사용
if [ -z "$MAX_WORKER_NUM" ]; then
    MAX_WORKER_NUM=$DEFAULT_WORKER_NUM
fi

cd $APP

n=0
while [ $n -lt 5 ]
do
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

exec supervisord -c /app/deploy/supervisord.conf
