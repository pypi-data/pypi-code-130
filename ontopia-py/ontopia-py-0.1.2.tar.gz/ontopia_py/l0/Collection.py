from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Entity import Entity

if TYPE_CHECKING:
    from rdflib import Graph


class Collection(Entity):
    __type__ = L0["Collection"]

    hasMember: List[Entity] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasMember:
            for hasMember in self.hasMember:
                g.add((self.uriRef, L0["hasMember"], hasMember.uriRef))
