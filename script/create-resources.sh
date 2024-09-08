# 데이터 볼륨 생성
sudo docker volume create \
  --driver local \
  --opt type=none \
  --opt o=bind \
  --opt device=$(dirname $(pwd))/backend/data/backend \
  backend-data

# 프론트엔드 로그 볼륨 생성
#sudo docker volume create \
#  --driver local \
#  --opt type=none \
#  --opt o=bind \
#  --opt device=$(dirname $(pwd))/frontend/deploy/log \
#  frontend-log-test
#
## 스케쥴러 로그 볼륨 생성
#sudo docker volume create \
#  --driver local \
#  --opt type=none \
#  --opt o=bind \
#  --opt device=$(dirname $(pwd))/scheduler/deploy/scheduler/logs \
#  scheduler-log-test
#
## 네트워크 생성
#sudo docker network create \
#  --driver overlay \
#  --attachable \
#  code-place-test-network
