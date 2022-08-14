from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Description import Description
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from ..Thing import Thing
    from ..ti.Duration import Duration
    from .Route import Route


class TripPlan(Description):
    __type__ = ROUTE["TripPlan"]

    hasRoute: List[Route] = None
    hasSubTripPlan: List[TripPlan] = None
    hasSuperTripPlan: List[TripPlan] = None
    hasEstimatedDuration: Duration = None
    isTripPlanOf: Thing = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasRoute:
            for hasRoute in self.hasRoute:
                g.add((self.uriRef, ROUTE["hasRoute"], hasRoute.uriRef))

        if self.hasSubTripPlan:
            for hasSubTripPlan in self.hasSubTripPlan:
                g.add(
                    (self.uriRef, ROUTE["hasSubTripPlan"], hasSubTripPlan.uriRef))

        if self.hasSuperTripPlan:
            for hasSuperTripPlan in self.hasSuperTripPlan:
                g.add(
                    (self.uriRef, ROUTE["hasSuperTripPlan"], hasSuperTripPlan.uriRef))

        if self.hasEstimatedDuration:
            g.add(
                (self.uriRef, ROUTE["hasEstimatedDuration"], self.hasEstimatedDuration.uriRef))

        if self.isTripPlanOf:
            g.add((self.uriRef, ROUTE["isTripPlanOf"],
                  self.isTripPlanOf.uriRef))
