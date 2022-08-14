from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .Channel import Channel

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class OtherElectronicChannel(Channel):
    __type__ = CPSV["OtherElectronicChannel"]

    accessReference: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.accessReference:
            g.add((self.uriRef, CPSV["accessReference"], self.accessReference))
