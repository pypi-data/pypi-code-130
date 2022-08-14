from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.EventOrSituation import EventOrSituation
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..ti.TimeInterval import TimeInterval
    from .PointOfInterest import PointOfInterest


class POINameInTime(EventOrSituation):
    __type__ = POI["POINameInTime"]

    isPOINameInTimeFor: PointOfInterest = None
    atTime: TimeInterval = None
    POIofficialName: List[Literal] = None
    POIalternativeName: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isPOINameInTimeFor:
            g.add((self.uriRef, POI["isPOINameInTimeFor"],
                  self.isPOINameInTimeFor.uriRef))

        if self.atTime:
            g.add((self.uriRef, TI["atTime"], self.atTime.uriRef))

        if self.POIofficialName:
            for POIofficialName in self.POIofficialName:
                g.add((self.uriRef, POI["POIofficialName"], POIofficialName))

        if self.POIalternativeName:
            for POIalternativeName in self.POIalternativeName:
                g.add(
                    (self.uriRef, POI["POIalternativeName"], POIalternativeName))
