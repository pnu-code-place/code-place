#!/bin/bash

###############################################################################
# 이 스크립트는 PostgreSQL 데이터베이스와 data 백업을 생성하고,
# AWS S3 버킷에 업로드하는 기능을 수행합니다.
#
# 주요 동작:
# 1. 현재 시간을 기준으로 백업 파일명을 생성합니다.
# 2. 환경 변수 파일(.env)에서 데이터베이스 및 AWS 정보를 불러옵니다.
# 3. 필요한 환경 변수가 모두 설정되어 있는지 확인합니다.
# 4. Docker 컨테이너 내부의 PostgreSQL 데이터베이스를 백업하고 gzip으로 압축하여 S3에 직접 업로드합니다.
# 5. 데이터 디렉토리들을 tar.gz로 압축하여 S3에 직접 업로드합니다.
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
#   POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, AWS_S3_BACKUP_BUCKET 등이 정의되어 있어야 합니다.
# - Docker와 AWS CLI가 설치되어 있어야 합니다.
# - AWS 관련 환경 변수가 모두 설정되어 있어야 합니다.
# - production 환경 데이터베이스만 백업하고, dev 환경은 백업하지 않도록 crontab을 실행해주세요.
###############################################################################

set -e

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
ENV_FILE="../deployment/.env"
DATABASE_CONTAINER_NAME="code-place-dev_oj-postgres"

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

# AWS S3 관련 환경 변수 확인
if [[ -z "$AWS_S3_BACKUP_BUCKET" || -z "$AWS_ACCESS_KEY_ID" || -z "$AWS_SECRET_ACCESS_KEY" ]]; then
    echo "AWS S3 environment variables are not set in $ENV_FILE"
    echo "Required: AWS_S3_BACKUP_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
    exit 1
fi

# AWS 환경 변수 설정
export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-ap-northeast-2}"

# PostgreSQL 데이터베이스 백업을 S3에 업로드
echo "Starting PostgreSQL backup to S3..."
export PGPASSWORD="$POSTGRES_PASSWORD"
docker exec $(docker ps -q -f name=$DATABASE_CONTAINER_NAME) pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" | \
    gzip | \
    aws s3 cp - "s3://$AWS_S3_BACKUP_BUCKET/postgres/$TIMESTAMP.sql.gz" --storage-class GLACIER

echo "PostgreSQL backup completed: s3://$AWS_S3_BACKUP_BUCKET/postgres/$TIMESTAMP.sql.gz"

# 데이터 디렉토리 백업을 S3에 직접 업로드
echo "Starting data directories backup to S3..."

DATA_TARGET_DIRS=(
    "assets"
    "backend"
    "config"
)
for dir in "${DATA_TARGET_DIRS[@]}"; do
    echo "Backing up directory: ./data/$dir"
    if [[ -d "./data/$dir" ]]; then
        tar -czf - "./data/$dir" | \
            aws s3 cp - "s3://$AWS_S3_BACKUP_BUCKET/data/$dir/$TIMESTAMP.tar.gz" --storage-class GLACIER
        echo "$dir backup completed: s3://$AWS_S3_BACKUP_BUCKET/data/$dir/$TIMESTAMP.tar.gz"
    else
        echo "Directory ./data/$dir does not exist, skipping backup."
    fi
done

echo "All backups completed successfully."
