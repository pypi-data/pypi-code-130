from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .DemographicEvent import DemographicEvent

if TYPE_CHECKING:
    from rdflib import Graph

    from .CivilStatusCategory import CivilStatusCategory


class CivilStatusEvent(DemographicEvent):
    __type__ = ONTOIM["CivilStatusEvent"]

    hasCivilStatusCategory: CivilStatusCategory = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasCivilStatusCategory:
            g.add(
                (self.uriRef, ONTOIM["hasCivilStatusCategory"], self.hasCivilStatusCategory.uriRef))
