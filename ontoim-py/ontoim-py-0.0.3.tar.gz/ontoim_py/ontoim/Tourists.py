from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .DemographicObservation import DemographicObservation

if TYPE_CHECKING:
    from rdflib import Graph

    from .TouristType import TouristType


class Tourists(DemographicObservation):
    __type__ = ONTOIM["Tourists"]

    hasTouristType: TouristType = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasTouristType:
            g.add(
                (self.uriRef, ONTOIM["hasTouristType"], self.hasTouristType.uriRef))
