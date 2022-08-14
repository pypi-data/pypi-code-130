from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Description import Description
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class Call(Description):
    __type__ = PROJ["Call"]

    name: List[Literal] = None
    identifier: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))

        if self.identifier:
            g.add((self.uriRef, L0["identifier"], self.identifier))
