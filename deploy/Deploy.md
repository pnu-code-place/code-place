# Deploy_Production

- 현재 CSEP FE Repository는 **Nginx**를 Web Server로 사용하고 있습니다.
- CSEP_BE/data/public 디렉토리 마운트를 해야 정상적으로 배포가 가능합니다.

---
## 1. FE build
```
npm run build
```

## 2. Dockerfile 이미지 빌드
```
cd ./deploy
docker build --tag csep:0.1 .
```

## 3. Docker Container Run
```
cd ..
docker run -v $(pwd):/CSEP_FE -p 80:80 csep:0.1
```
