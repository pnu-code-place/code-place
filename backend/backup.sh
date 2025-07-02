#!/bin/bash

###############################################################################
# 이 스크립트는 PostgreSQL 데이터베이스의 백업을 자동으로 생성하고,
# 생성된 백업 파일을 AWS S3 버킷에 업로드하는 기능을 수행합니다.
#
# 주요 동작:
# 1. 현재 시간을 기준으로 백업 파일명을 생성합니다.
# 2. 환경 변수 파일(.env)에서 데이터베이스 및 AWS 정보를 불러옵니다.
# 3. 필요한 환경 변수가 모두 설정되어 있는지 확인합니다.
# 4. Docker 컨테이너 내부의 PostgreSQL 데이터베이스를 백업하고 gzip으로 압축합니다.
# 5. (선택) AWS S3 관련 환경 변수가 모두 설정되어 있다면, S3 버킷으로 백업 파일을 업로드합니다.
#
# 리눅스에서 crontab을 이용해 이 스크립트를 정기적으로 자동 실행할 수 있습니다.
# 예를 들어, 매일 오전 2시에 실행하려면 아래와 같이 등록하세요:
#
#   crontab -e
#   0 2 * * * PATH_TO_CODE_PLACE/backend/backup.sh
#
# (스크립트에 실행 권한이 필요합니다: chmod +x PATH_TO_CODE_PLACE/backend/backup.sh)
#
# 주의사항:
# - 환경 변수 파일(.env)이 ../deployment/.env 경로에 있어야 하며,
#   POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, AWS_S3_BUCKET 등이 정의되어 있어야 합니다.
# - Docker와 AWS CLI가 설치되어 있어야 하며, 백업 대상 컨테이너 이름이 'code-place-dev_oj-postgres'로 되어 있어야 합니다.
# - S3 업로드는 AWS 관련 환경 변수가 모두 설정된 경우에만 수행됩니다.
###############################################################################

set -e

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

ENV_FILE="../deployment/.env"
BACKUP_DIR="./data/backup/"
BACKUP_GZ_FILE="postgres_backup_$TIMESTAMP.sql.gz"
RETENTION_DAYS=30

# 백업 디렉토리가 존재하지 않으면 생성
if [[ ! -d "$BACKUP_DIR" ]]; then
    mkdir -p "$BACKUP_DIR"
fi

# 환경 변수 파일이 존재하는지 확인
if [[ ! -f "$ENV_FILE" ]]; then
    echo "Environment file not found: $ENV_FILE"
    exit 1
fi

source "$ENV_FILE"

# 데이터베이스 관련 환경 변수 확인
if [[ -z "$POSTGRES_DB" || -z "$POSTGRES_USER" || -z "$POSTGRES_PASSWORD" ]]; then
    echo "Database environment variables are not set in $ENV_FILE"
    exit 1
fi

export PGPASSWORD="$DB_PASSWORD"
docker exec $(docker ps -q -f name=code-place-dev_oj-postgres) pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" | gzip > "$BACKUP_DIR$BACKUP_GZ_FILE"

# AWS S3 관련 환경 변수가 없는 경우 업로드 스킵
if [[ ! -n "$AWS_S3_BUCKET" || ! -n "$AWS_ACCESS_KEY_ID" || ! -n "$AWS_SECRET_ACCESS_KEY" ]]; then
    exit 0
fi

POSTGRES_BACKUP_DIR="postgres/"
export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-ap-northeast-2}"

# AWS S3 버킷에 백업 파일 업로드
aws s3 cp "$BACKUP_DIR$BACKUP_GZ_FILE" "s3://$AWS_S3_BUCKET/$POSTGRES_BACKUP_DIR$BACKUP_GZ_FILE" --storage-class GLACIER
