"""Mongo module."""

from bson import ObjectId
from typing import Dict
from logging import getLogger

from motor.motor_asyncio import (
    AsyncIOMotorClient as AsyncClient,
    AsyncIOMotorDatabase as AsyncDatabase,
)

from spec.types import Module

log = getLogger(__name__)

DEFAULT_URI = 'mongodb://localhost'
DEFAULT_POOL_SIZE = 10

CLIENTS: Dict[str, AsyncClient] = dict()
COLLECTIONS: Dict[str, AsyncDatabase] = dict()


class Mongo(Module):
    """Mongo module."""

    module_settings = {
        'uri': DEFAULT_URI,
        'collection': 'test_collection',
        'pool_size': DEFAULT_POOL_SIZE,
    }

    async def prepare(self, scope):  # noqa
        """Test prepare hook."""
        log.warning(
            f'Mongo connection `{self.collection_name}` prepare',
            extra={
                'alias': self.alias,
                'scope': scope,
                'collection': self.collection_name,
            },
        )

        _uri = self.module_settings.get('uri', DEFAULT_URI)
        _psize = self.module_settings.get('pool_size', DEFAULT_POOL_SIZE)
        _client = AsyncClient(_uri, maxPoolSize=_psize, minPoolSize=_psize)

        CLIENTS[self.composite_name] = _client
        COLLECTIONS[self.composite_name] = _client[self.collection_name]

    async def release(self, scope):  # noqa
        """Test release hook."""
        log.warning(
            f'Mongo connection `{self.collection_name}` release',
            extra={
                'alias': self.alias,
                'scope': scope,
                'collection': self.collection_name,
            }
        )

        CLIENTS[self.composite_name].close()

    @property
    def db(self) -> AsyncDatabase:
        """Async db collection."""
        return COLLECTIONS[self.composite_name]

    @property
    def collection_name(self) -> str:
        """Get collection name."""
        _name = self.module_settings.get('collection')
        assert _name, 'Empty collection name'
        return _name

    @property
    def composite_name(self) -> str:
        """Composite name."""
        return f'{self.alias}.{self.collection_name}'


class Primary(str):
    """Primary object id."""

    @classmethod
    def __get_validators__(cls):
        """Primary validators."""
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Validate primary."""
        if v == '':
            raise TypeError('ObjectId is empty')
        if ObjectId.is_valid(v) is False:
            raise TypeError('ObjectId invalid')
        return str(v)


__all__ = (
    'AsyncDatabase',
    'AsyncClient',
    'ObjectId',
    'Primary',
    'Mongo',
)
