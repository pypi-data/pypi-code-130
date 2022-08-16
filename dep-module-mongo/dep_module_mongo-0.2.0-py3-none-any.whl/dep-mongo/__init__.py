"""Mongo module."""

from bson import ObjectId
from logging import getLogger

from spec.types import Module


log = getLogger(__name__)


class Mongo(Module):
    """Mongo module."""

    alias = 'mongo'

    async def middleware(self, scope, receive, send, app=None):  # noqa
        """Test http middleware."""
        log.warning(
            'Mongo middleware',
            extra={'scope': scope, 'receive': receive, 'send': send},
        )

        return await app(scope, receive, send)

    async def prepare(self, scope):  # noqa
        """Test prepare hook."""
        log.warning('Mongo prepare', extra={'scope': scope})

    async def release(self, scope):  # noqa
        """Test release hook."""
        log.warning('Mongo release', extra={'scope': scope})


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
    'ObjectId',
    'Primary',
    'Mongo',
)
