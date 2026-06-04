#!/bin/sh

DATA=/data # 데이터 디렉토리 경로 설정

# config, test_case, avatar, banner, popup 디렉토리 생성
mkdir -p $DATA/config $DATA/test_case $DATA/public/upload $DATA/public/avatar $DATA/public/website $DATA/public/banner $DATA/public/popup

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

: "${MAX_WORKER_NUM:=1}"

cd /app

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
python3 manage.py loaddata /app/fixtures/*.json
echo "Fixtures loaded!"

addgroup -g 903 spj
adduser -u 900 -S -G spj server

chown -R server:spj $DATA /app/dist
find $DATA/test_case -type d -exec chmod 710 {} \;
find $DATA/test_case -type f -exec chmod 640 {} \;

exec gunicorn oj.wsgi \
    --user server \
    --group spj \
    --bind 0.0.0.0:8080 \
    --workers "$MAX_WORKER_NUM" \
    --threads 4 \
    --max-requests-jitter 10000 \
    --max-requests 1000000 \
    --keep-alive 32 \
    --access-logfile - \
    --error-logfile - \
    --capture-output
