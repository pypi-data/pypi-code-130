"""Mongo plugin."""

from typing import Dict
from spec.types import App, Plugin, Spec

from logging import getLogger

# from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

log = getLogger(__name__)

async def prepare(app: App, alias: str, spec: Spec, options: Dict = None):
    log.warning(f'PREPAAAAAARE {options}')


async def release(app: App, alias: str, spec: Spec, options: Dict = None):
    log.warning(f'RELEEEASE {options}')


class MongoPlugin(Plugin):
    """Mongo plugin."""

    type_name = 'mongo'

    on_prepare = prepare
    on_release = release
