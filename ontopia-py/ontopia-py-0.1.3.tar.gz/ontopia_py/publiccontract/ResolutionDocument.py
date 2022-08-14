from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .AmendmentDocument import AmendmentDocument

if TYPE_CHECKING:
    from rdflib import Graph

    from .ResolutionReason import ResolutionReason


class ResolutionDocument(AmendmentDocument):
    __type__ = PUBC["ResolutionDocument"]

    resolutionReason: List[ResolutionReason] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.resolutionReason:
            for resolutionReason in self.resolutionReason:
                g.add(
                    (self.uriRef, PUBC["resolutionReason"], resolutionReason.uriRef))
