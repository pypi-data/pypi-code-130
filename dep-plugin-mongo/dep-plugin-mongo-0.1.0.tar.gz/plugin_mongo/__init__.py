"""Plugin mongo."""

from bson import ObjectId

from .plugin import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    CLIENTS,
    CONNECTIONS,
    MongoPlugin,
)


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
    'AsyncIOMotorClient',
    'AsyncIOMotorDatabase',
    'CLIENTS',
    'CONNECTIONS',
    'ObjectId',
    'Primary',
    'MongoPlugin',
)
