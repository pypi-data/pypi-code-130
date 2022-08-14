from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .DemographicObservation import DemographicObservation

if TYPE_CHECKING:
    from rdflib import Graph

    from .CivilStatusCategory import CivilStatusCategory


class CivilStatus(DemographicObservation):
    __type__ = ONTOIM["CivilStatus"]

    hasCivilStatusCategory: CivilStatusCategory = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasCivilStatusCategory:
            g.add(
                (self.uriRef, ONTOIM["hasCivilStatusCategory"], self.hasCivilStatusCategory.uriRef))
