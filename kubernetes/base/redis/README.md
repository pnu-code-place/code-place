# Redis HA 배포 가이드

이 디렉터리는 Opstree Redis Operator를 사용해 Redis를 HA 구성으로 배포합니다.

## 구성

- `RedisReplication`: Redis 3개 Pod로 master/replica 구성을 만듭니다.
- `RedisSentinel`: Sentinel 3개 Pod로 master 감시와 failover를 수행합니다.
- 애플리케이션은 `redis-sentinel:26379`로 접속하고, master group 이름은 `myMaster`를 사용합니다.

## 사전 조건

클러스터에 Redis Operator가 설치되어 있어야 합니다.

```sh
helm repo add ot-helm https://ot-container-kit.github.io/helm-charts/
helm repo update
helm install redis-operator ot-helm/redis-operator
```

## 배포

Kustomize base 또는 overlay를 적용하면 `redis.yaml`이 함께 배포됩니다.

```sh
kubectl apply -k kubernetes/overlays/prod
```

Redis만 직접 적용할 수도 있습니다.

```sh
kubectl apply -f kubernetes/base/redis/redis.yaml
```

## 애플리케이션 설정

backend, celery worker, celery beat는 다음 환경변수로 Sentinel을 사용합니다.

```sh
REDIS_HOST=redis-sentinel
REDIS_PORT=26379
REDIS_USE_SENTINEL=1
REDIS_SENTINEL_MASTER_NAME=myMaster
REDIS_SENTINEL_HOSTS=redis-sentinel:26379
```

## 운영 메모

Redis와 Sentinel Pod는 `kubernetes.io/hostname` 기준으로 서로 다른 노드에 분산되도록 설정되어 있습니다. 이 구성은 최소 3개 이상의 스케줄 가능한 Kubernetes 노드를 전제로 합니다. 노드가 3개 미만이면 HA를 만족할 수 없으므로 Pod가 pending 상태로 남을 수 있습니다.

Sentinel failover는 Redis master 장애 시 자동 승격을 수행하지만, failover 중에는 짧은 연결 재시도 구간이 생길 수 있습니다. 완전한 무중단에 가깝게 운영하려면 Longhorn replica와 Kubernetes 노드 장애 조건이 맞는지, 애플리케이션 retry 정책이 충분한지 함께 점검해야 합니다.
