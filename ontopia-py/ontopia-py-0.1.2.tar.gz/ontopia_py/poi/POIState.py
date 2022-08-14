from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .PointOfInterest import PointOfInterest


class POIState(Characteristic):
    __type__ = POI["POIState"]

    POIstate: List[Literal] = None
    isPOIStateFor: List[PointOfInterest] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.POIstate:
            for POIstate in self.POIstate:
                g.add((self.uriRef, POI["POIstate"], POIstate))

        if self.isPOIStateFor:
            for isPOIStateFor in self.isPOIStateFor:
                g.add(
                    (self.uriRef, POI["isPOIStateFor"], isPOIStateFor.uriRef))
