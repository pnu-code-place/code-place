from django.core.cache import cache, caches    # noqa
from django.conf import settings    # noqa

from django_redis.cache import RedisCache
from django_redis.client import SentinelClient
from django_redis.client.default import DefaultClient


class MyRedisClientMixin:

    def __getattr__(self, item):
        client = self.get_client(write=True)
        return getattr(client, item)

    def redis_incr(self, key, count=1):
        """
        django 默认的 incr 在 key 不存在时候会抛异常
        """
        client = self.get_client(write=True)
        return client.incr(key, count)


class MyRedisClient(MyRedisClientMixin, DefaultClient):
    pass


class MyRedisSentinelClient(MyRedisClientMixin, SentinelClient):
    pass


class MyRedisCache(RedisCache):

    def __init__(self, server, params):
        super().__init__(server, params)
        options = params.get("OPTIONS", {})
        client_class = options.get("CLIENT_CLASS")
        if client_class == "django_redis.client.SentinelClient":
            self._client_cls = MyRedisSentinelClient
        else:
            self._client_cls = MyRedisClient

    def __getattr__(self, item):
        return getattr(self.client, item)
