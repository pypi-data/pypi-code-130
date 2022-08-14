from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .Object import Object

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class Description(Object):
    __type__ = L0["Description"]

    description: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.description:
            g.add((self.uriRef, L0["description"], self.description))
