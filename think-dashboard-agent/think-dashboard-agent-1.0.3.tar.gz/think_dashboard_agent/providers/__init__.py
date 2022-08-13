from .database import DatabaseProvider
from .elasticsearch import ElasticSearchProvider
from .redis_provider import RedisProvider
from .ssl_provider import SSLProvider
from .base import BaseProvider

DEFAULT_PROVIDERS = {
    'database': DatabaseProvider,
    'redis': RedisProvider,
    'elasticsearch': ElasticSearchProvider,
    'ssl': SSLProvider
}

__all__ = [
    'BaseProvider',
    'DatabaseProvider',
    'RedisProvider',
    'ElasticSearchProvider',
    'SSLProvider',
    'DEFAULT_PROVIDERS'
]
