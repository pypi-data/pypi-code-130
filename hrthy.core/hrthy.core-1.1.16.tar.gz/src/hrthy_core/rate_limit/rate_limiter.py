from datetime import datetime

from starlette.requests import Request

from hrthy_core.rate_limit.exceptions import TooManyRequestsException
from hrthy_core.rate_limit.rate_limit_configuration import RateLimiterConfig
from hrthy_core.utils.utils import logger


class RateLimiter:

    def __init__(
        self,
        cache_key_prefix: str,
        times: int,
        seconds: int = None,
        minutes: int = None,
        hours: int = None,
        days: int = None
    ):
        """
        :param cache_key_prefix: request prefix
        :param limit: expressed in "number/seconds"
        """
        self.cache_key_prefix = cache_key_prefix
        if not any([seconds, minutes, hours, days]) or times <= 0:
            raise Exception('Wrong Rate Limit configuration')
        self.period = seconds + minutes * 60 + hours * 3600 + days * 86400
        self.times = times

    def __call__(self, request: Request):
        ip = request.headers.get('X-Forwarded-For') or request.client.host
        self._apply_rate_limit(ip)

    def _apply_rate_limit(self, rate_limit_identifier: str):
        cache_key: str = f"{RateLimiterConfig.cache_prefix}:{self.cache_key_prefix}:{rate_limit_identifier}"
        call_counter: int = RateLimiterConfig.redis.get(cache_key) or 0
        call_counter = int(call_counter) + 1
        if call_counter > self.times:
            expire_at: int = RateLimiterConfig.redis.expiretime(cache_key)
            now = datetime.utcnow().timestamp()
            logger.info(
                'Rate limit hit. Key: %s, Times: %s, Period: %s' % (rate_limit_identifier, self.times, self.period)
                )
            raise TooManyRequestsException(
                detail="Too many requests",
                headers={
                    'A Retry-After': expire_at - now
                }
            )
        RateLimiterConfig.redis.set(name=cache_key, value=call_counter, ex=self.period)
