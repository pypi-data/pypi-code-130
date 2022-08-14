from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .OSDCriterion import OSDCriterion
    from .OSDFeature import OSDFeature


class OfferedServiceDescription(Object):
    __type__ = ACCO["OfferedServiceDescription"]

    maxValue: List[Literal] = None
    minValue: List[Literal] = None
    totalValue: List[Literal] = None
    genericValue: Literal = None
    hasOSDCriterion: List[OSDCriterion] = None
    hasOSDFeature: List[OSDFeature] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.maxValue:
            for maxValue in self.maxValue:
                g.add((self.uriRef, ACCO["maxValue"], maxValue))

        if self.minValue:
            for minValue in self.minValue:
                g.add((self.uriRef, ACCO["minValue"], minValue))

        if self.totalValue:
            for totalValue in self.totalValue:
                g.add((self.uriRef, ACCO["totalValue"], totalValue))

        if self.genericValue:
            g.add((self.uriRef, ACCO["genericValue"], self.genericValue))

        if self.hasOSDCriterion:
            for hasOSDCriterion in self.hasOSDCriterion:
                g.add(
                    (self.uriRef, ACCO["hasOSDCriterion"], hasOSDCriterion.uriRef))

        if self.hasOSDFeature:
            for hasOSDFeature in self.hasOSDFeature:
                g.add(
                    (self.uriRef, ACCO["hasOSDFeature"], hasOSDFeature.uriRef))
