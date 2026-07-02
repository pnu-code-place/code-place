#!/bin/sh

mkdir -p /data/config

if [ ! -f "/data/config/secret.key" ]; then
    echo `cat /dev/urandom | head -1 | md5sum | head -c 32` > /data/config/secret.key
fi

cd /app

exec celery -A oj worker --loglevel=info --pool=solo --concurrency=1
