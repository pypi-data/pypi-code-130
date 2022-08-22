from datetime import datetime

from starlette.requests import Request

from hrthy_core.rate_limit.exceptions import TooManyRequestsException
from hrthy_core.rate_limit.rate_limit_configuration import RateLimiterConfig


class RateLimiter:

    def __init__(
        self,
        cache_key_prefix: str,
        limit: str
    ):
        """
        :param cache_key_prefix: request prefix
        :param limit: expressed in "number/seconds"
        """
        self.cache_key_prefix = cache_key_prefix
        limit = limit.split('/')
        if len(limit) != 2 or not limit[0].isdigit() or not limit[1].isdigit():
            raise Exception('Wrong Rate Limit configuration')
        self.allowed_requests_count = int(limit[0])
        self.time_period = int(limit[1])

    def __call__(self, request: Request):
        ip = request.headers.get('X-Forwarded-For') or request.client.host
        self._apply_rate_limit(ip)

    def _apply_rate_limit(self, rate_limit_identifier: str):
        cache_key: str = f"{RateLimiterConfig.cache_prefix}:{self.cache_key_prefix}:{rate_limit_identifier}"
        call_counter: int = RateLimiterConfig.redis.get(cache_key) or 0
        call_counter = int(call_counter) + 1
        if call_counter > self.allowed_requests_count:
            expire_at: int = RateLimiterConfig.redis.expiretime(cache_key)
            now = datetime.utcnow().timestamp()
            raise TooManyRequestsException(
                detail="Too many requests",
                headers={
                    'A Retry-After': expire_at - now
                }
            )
        RateLimiterConfig.redis.set(name=cache_key, value=call_counter, ex=self.time_period)
