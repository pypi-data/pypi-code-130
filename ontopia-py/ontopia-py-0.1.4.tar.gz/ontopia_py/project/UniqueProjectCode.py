from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class Programme(Object):
    __type__ = PROJ["Programme"]

    uniqueProjectCodeValue: Literal = None
    uniqueProjectCodeType: Literal = None  # { "linked" , "master" , "normal" }

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.uniqueProjectCodeValue:
            g.add(
                (self.uriRef, PROJ["uniqueProjectCodeValue"], self.uniqueProjectCodeValue))

        if self.uniqueProjectCodeType:
            g.add(
                (self.uriRef, PROJ["uniqueProjectCodeType"], self.uniqueProjectCodeType))
