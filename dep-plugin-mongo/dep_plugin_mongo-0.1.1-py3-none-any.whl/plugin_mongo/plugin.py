"""Mongo plugin."""

from typing import Dict
from spec.types import App, Plugin, Spec

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


CLIENTS: Dict[str, AsyncIOMotorClient] = {}
CONNECTIONS: Dict[str, AsyncIOMotorDatabase] = {}


class MongoPlugin(Plugin):
    """Mongo plugin."""

    type_name = 'mongo'

    async def prepare(self, app: App, spec: Spec):
        """Prepare mongo."""
        uri = self.env_options.get('uri')
        pool_size = int(
            self.env_options.get(
                'pool_size',
                spec.policy.db_pool_size,
            )
        )

        client_options = {'minPoolSize': pool_size, 'maxPoolSize': pool_size}

        if self.fqdn not in CLIENTS:
            CLIENTS[self.fqdn] = AsyncIOMotorClient(uri, **client_options)

        CONNECTIONS[self.fqdn] = CLIENTS[self.fqdn][self.alias]

    async def release(self, app: App, spec: Spec):
        """Release mongo."""
        CLIENTS[self.fqdn].close()
