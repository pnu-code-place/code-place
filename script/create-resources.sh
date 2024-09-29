# 데이터 볼륨 생성
sudo docker volume create \
  --driver local \
  --opt type=none \
  --opt o=bind \
  --opt device=$(dirname $(pwd))/backend/data/backend \
  backend-data-prod
