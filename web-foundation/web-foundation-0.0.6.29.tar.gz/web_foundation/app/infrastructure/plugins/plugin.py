from __future__ import annotations

import asyncio
import inspect
from importlib.util import module_from_spec
from types import ModuleType

import loguru


class Plugin:
    source: str
    imported: ModuleType | None

    target: str
    name: str
    filename: str
    enable: bool

    before: bool = False
    override: bool = False
    after: bool = False

    def __init__(self, name: str, source: str):
        self.name = name
        self.filename = name
        self.source = source
        self.target = ""

    def import_it(self, spec):
        imported = module_from_spec(spec)
        spec.loader.exec_module(imported)
        self.imported = imported
        if hasattr(self.imported, "before"):
            self.before = True
        if hasattr(self.imported, "after"):
            self.after = True
        if hasattr(self.imported, "override"):
            self.override = True

    def drop_imported(self):
        self.imported = None
        self.before = False
        self.override = False
        self.after = False

    async def exec_before(self, context, container):
        if self.before:
            await self.imported.before(context, container)

    async def exec_after(self, context, container, target_result):
        if self.after:
            await self.imported.after(target_result)

    async def exec_override(self, context, container):
        if self.override:
            await self.imported.override(context, container)

    def __repr__(self):
        return f"Plugin({self.name} on {self.target})"

    def __eq__(self, other: Plugin):
        return self.name == other.name and self.target == other.target
