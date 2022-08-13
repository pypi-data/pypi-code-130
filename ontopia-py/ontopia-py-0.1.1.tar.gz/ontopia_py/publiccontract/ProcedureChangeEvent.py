from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.EventOrSituation import EventOrSituation
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .EconomicSummary import EconomicSummary


class ProcedureChangeEvent(EventOrSituation):
    __type__ = PUBC["ProcedureChangeEvent"]

    hasOriginalSummary: List[EconomicSummary] = None
    hasResultingSummary: List[EconomicSummary] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasOriginalSummary:
            for hasOriginalSummary in self.hasOriginalSummary:
                g.add(
                    (self.uriRef, PUBC["hasOriginalSummary"], hasOriginalSummary.uriRef))

        if self.hasResultingSummary:
            for hasResultingSummary in self.hasResultingSummary:
                g.add(
                    (self.uriRef, PUBC["hasResultingSummary"], hasResultingSummary.uriRef))
