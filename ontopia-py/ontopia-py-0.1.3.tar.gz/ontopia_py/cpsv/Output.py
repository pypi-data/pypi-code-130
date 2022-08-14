from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .ServiceInputOutputType import ServiceInputOutputType


class Output(Object):
    __type__ = CPSV["Output"]

    hasServiceInputOutputType: List[ServiceInputOutputType] = None
    name: List[Literal] = None
    description: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasServiceInputOutputType:
            for hasServiceInputOutputType in self.hasServiceInputOutputType:
                g.add(
                    (self.uriRef, CPSV["hasServiceInputOutputType"], hasServiceInputOutputType.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))
