from __future__ import annotations

from typing import TYPE_CHECKING

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class Document(Object):
    __type__ = PUBC["Document"]

    identifier: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.identifier:
            g.add((self.uriRef, L0["identifier"], self.identifier))
