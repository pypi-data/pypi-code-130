from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from ..Thing import Thing


class Image(Object):
    __type__ = SM["Image"]

    isImageOf: List[Thing] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isImageOf:
            for isImageOf in self.isImageOf:
                g.add((self.uriRef, SM["isImageOf"], isImageOf.uriRef))
