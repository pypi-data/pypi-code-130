from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Activity import Activity
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .AmendmentDocument import AmendmentDocument
    from .EconomicSummary import EconomicSummary
    from .Notice import Notice


class ProcurementProject(Activity):
    __type__ = PUBC["ProcurementProject"]

    hasChangeDocument: List[AmendmentDocument] = None
    hasEconomicSummary: List[EconomicSummary] = None
    hasNotice: List[Notice] = None
    description: List[Literal] = None
    auctionBaseAmount: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasChangeDocument:
            for hasChangeDocument in self.hasChangeDocument:
                g.add(
                    (self.uriRef, PUBC["hasChangeDocument"], hasChangeDocument.uriRef))

        if self.hasEconomicSummary:
            for hasEconomicSummary in self.hasEconomicSummary:
                g.add(
                    (self.uriRef, PUBC["hasEconomicSummary"], hasEconomicSummary.uriRef))

        if self.hasNotice:
            for hasNotice in self.hasNotice:
                g.add((self.uriRef, PUBC["hasNotice"], hasNotice.uriRef))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.auctionBaseAmount:
            for auctionBaseAmount in self.auctionBaseAmount:
                g.add(
                    (self.uriRef, PUBC["auctionBaseAmount"], auctionBaseAmount))
