from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class Programme(Object):
    __type__ = PROJ["Programme"]

    description: List[Literal] = None
    identifier: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.identifier:
            g.add((self.uriRef, L0["identifier"], self.identifier))
