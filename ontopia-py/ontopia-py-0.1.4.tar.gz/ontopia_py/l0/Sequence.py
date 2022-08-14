from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .Collection import Collection

if TYPE_CHECKING:
    from rdflib import Graph

    from .Entity import Entity


class Sequence(Collection):
    __type__ = L0["Sequence"]

    hasFirstMember: Entity = None
    hasLastMember: Entity = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasFirstMember:
            g.add((self.uriRef, L0["hasFirstMember"],
                  self.hasFirstMember.uriRef))

        if self.hasLastMember:
            g.add((self.uriRef, L0["hasLastMember"],
                  self.hasLastMember.uriRef))
