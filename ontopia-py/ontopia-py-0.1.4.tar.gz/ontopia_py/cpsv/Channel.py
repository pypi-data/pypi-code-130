from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from ..accesscondition.AccessCondition import AccessCondition
    from .ChannelType import ChannelType
    from .Cost import Cost
    from .Service import Service


class Channel(Object):
    __type__ = CPSV["Channel"]

    hasCost: List[Cost] = None
    isChannelOf: List[Service] = None
    hasChannelType: ChannelType = None
    hasAccessCondition: AccessCondition = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasCost:
            for hasCost in self.hasCost:
                g.add((self.uriRef, CPSV["hasCost"], hasCost.uriRef))

        if self.isChannelOf:
            for isChannelOf in self.isChannelOf:
                g.add((self.uriRef, CPSV["isChannelOf"], isChannelOf.uriRef))

        if self.hasChannelType:
            g.add((self.uriRef, CPSV["hasChannelType"],
                  self.hasChannelType.uriRef))

        if self.hasAccessCondition:
            g.add(
                (self.uriRef, ACOND["hasAccessCondition"], self.hasAccessCondition.uriRef))
