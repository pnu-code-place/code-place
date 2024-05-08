#! /bin/bash

# 데이터베이스에 College와 Department 데이터가 이미 로드되었는지 확인
if [ "$(echo "from account.models import College, Department; print(College.objects.count() == 0 or Department.objects.count() == 0)" | python manage.py shell)" == "True" ]; then
  sleep 2
  echo "Loading Fixtures..."
  python3 manage.py loaddata ./fixtures/*.json
  echo "Fixtures loaded!"
fi