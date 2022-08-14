from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from ..route.TripPlan import TripPlan

if TYPE_CHECKING:
    from rdflib import Graph

    from ..ti.TemporalEntity import TemporalEntity
    from .Path import Path
    from .TravellingMethod import TravellingMethod


class PathPlan(TripPlan):
    __type__ = PATHS["PathPlan"]

    bestWhen: List[TemporalEntity] = None
    hasTravellingMethod: TravellingMethod = None
    isTripPlanOf: Path = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.bestWhen:
            for bestWhen in self.bestWhen:
                g.add((self.uriRef, PATHS["bestWhen"], bestWhen.uriRef))

        if self.hasTravellingMethod:
            g.add(
                (self.uriRef, PATHS["hasTravellingMethod"], self.hasTravellingMethod.uriRef))

        if self.isTripPlanOf:
            g.add(
                (self.uriRef, ROUTE["isTripPlanOf"], self.isTripPlanOf.uriRef))
