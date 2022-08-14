from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from ..poi.PointOfInterest import PointOfInterest

if TYPE_CHECKING:
    from rdflib import Graph

    from .PathStage import PathStage


class Restaurant(PointOfInterest):
    __type__ = PATHS["Restaurant"]

    isNearbyRestaurantOf: List[PathStage] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isNearbyRestaurantOf:
            for isNearbyRestaurantOf in self.isNearbyRestaurantOf:
                g.add(
                    (self.uriRef, PATHS["isNearbyRestaurantOf"], isNearbyRestaurantOf.uriRef))
