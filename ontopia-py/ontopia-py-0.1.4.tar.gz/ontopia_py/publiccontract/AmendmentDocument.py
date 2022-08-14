from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .ProcurementDocument import ProcurementDocument

if TYPE_CHECKING:
    from rdflib import Graph

    from .AmendmentRationale import AmendmentRationale


class AmendmentDocument(ProcurementDocument):
    __type__ = PUBC["AmendmentDocument"]

    hasAmendmentRationale: List[AmendmentRationale] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasAmendmentRationale:
            for hasAmendmentRationale in self.hasAmendmentRationale:
                g.add(
                    (self.uriRef, PUBC["hasAmendmentRationale"], hasAmendmentRationale.uriRef))
