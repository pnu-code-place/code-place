#!/bin/sh

SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)" # 현재 스크립트 경로
TESTCASE_PATH="$(cd "$SCRIPT_PATH/../.." && pwd)/data/backend/test_case" # 기존 테스트케이스 경로
AVATAR_PATH="$(cd "$SCRIPT_PATH/../.." && pwd)/data/backend/public/avatar" # 기존 아바타 경로

echo $TESTCASE_PATH

DB_BACKUP_PATH=$SCRIPT_PATH/db # 데이터베이스 백업 경로
TESTCASE_BACKUP_PATH=$SCRIPT_PATH/testcase # 테스트케이스 백업 경로
AVATAR_BACKUP_PATH=$SCRIPT_PATH/avatar # 유저 아바타 백업 경로

CURRENT_TIME=$(date -Iseconds) # 현재 시간

echo "Backup Start..."

# 데이터베이스 데이터 백업
sudo docker compose exec -T oj-postgres pg_dumpall -c -U csep > $DB_BACKUP_PATH/"db-$CURRENT_TIME.sql"

# 테스트케이스 백업
sudo tar -cf $TESTCASE_BACKUP_PATH/"testcase-$CURRENT_TIME.tar" $TESTCASE_PATH

# default 아바타를 제외한 유저 아바타 백업
sudo tar -cf $AVATAR_BACKUP_PATH/"avatar-$CURRENT_TIME.tar" $AVATAR_PATH

echo "Backup Finished!"