from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Topic import Topic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .PointOfInterest import PointOfInterest


class PointOfInterestCategory(Topic):
    __type__ = POI["PointOfInterestCategory"]

    POIcategoryName: List[Literal] = None
    isPOICategoryFor: List[PointOfInterest] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.POIcategoryName:
            for POIcategoryName in self.POIcategoryName:
                g.add((self.uriRef, POI["POIcategoryName"], POIcategoryName))

        if self.isPOICategoryFor:
            for isPOICategoryFor in self.isPOICategoryFor:
                g.add(
                    (self.uriRef, POI["isPOICategoryFor"], isPOICategoryFor.uriRef))
