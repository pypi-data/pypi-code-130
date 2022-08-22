from redis.client import Redis


class RateLimiterConfig:
    redis: Redis = None
    cache_prefix: str = 'rate-limit'

    @classmethod
    async def init(
        cls,
        redis: Redis,
        cache_prefix: str
    ):
        cls.redis = redis
        cls.cache_prefix = cache_prefix
