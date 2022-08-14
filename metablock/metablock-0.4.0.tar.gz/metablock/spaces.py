from typing import Dict

from aiohttp.formdata import FormData

from .components import Component, CrudComponent, MetablockEntity


# Space
class Space(MetablockEntity):
    """Object representing a space"""

    @property
    def blocks(self) -> "SpaceBlocks":
        return SpaceBlocks(self, "services")

    @property
    def services(self) -> "SpaceBlocks":
        return self.blocks

    @property
    def extensions(self) -> "SpaceExtensions":
        return SpaceExtensions(self, "extensions")


class Spaces(CrudComponent):
    """Spaces"""

    Entity = Space


# Service
class Block(MetablockEntity):
    """Object representing a block in a space"""

    @property
    def plugins(self):
        return BlockPlugins(self, "plugins")

    @property
    def deployments(self):
        return CrudComponent(self, "deployments")

    async def config(self, *, callback=None) -> Dict:
        return await self.get(f"{self.url}/config", callback=callback)

    async def ship(self, name: str, bundle: str, env="stage", *, callback=None) -> Dict:
        data = FormData()
        data.add_field("name", name)
        data.add_field("bundle", open(bundle, "rb"), filename=bundle)
        data.add_field("env", env)
        return await self.post(f"{self.url}/deployments", data=data, callback=callback)

    async def add_route(self, *, callback=None, **kwargs) -> Dict:
        """Add a new route to the block"""
        return await self.post(f"{self.url}/routes", json=kwargs, callback=callback)

    async def update_route(self, name: str, *, callback=None, **kwargs) -> Dict:
        """Update a route in the block"""
        return await self.patch(
            f"{self.url}/routes/{name}", json=kwargs, callback=callback
        )


# For backward compatibility
Service = Block


class Blocks(CrudComponent):
    """Services"""

    Entity = Block


class SpaceBlocks(Blocks):
    def list_create_url(self) -> str:
        return "%s/%s" % (self.root.url, self.name)


# SpaceExtension
class SpaceExtension(MetablockEntity):
    """Object representing an SpaceExtension"""


class SpaceExtensions(CrudComponent):
    Entity = SpaceExtension

    def list_create_url(self) -> str:
        return "%s/%s" % (self.root.url, self.name)

    def delete_url(self, id_name: str) -> str:
        return f"{self.parent_url}/{id_name}"


# ServicePlugin


class BlockPlugin(MetablockEntity):
    """Object representing an ServicePlugin"""


class BlockPlugins(CrudComponent):
    Entity = BlockPlugin

    def list_create_url(self) -> str:
        return "%s/%s" % (self.root.url, self.name)


# Domain


class Domains(Component):
    async def check(self, domain: str) -> str:
        return await self.cli.get(f"{self.url}/check/{domain}")
