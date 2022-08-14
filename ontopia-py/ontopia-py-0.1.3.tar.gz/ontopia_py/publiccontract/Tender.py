from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Entity import Entity
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from ..l0.Agent import Agent
    from .Lot import Lot
    from .TenderDocument import TenderDocument
    from .TenderSubmission import TenderSubmission


class Tender(Entity):
    __type__ = PUBC["Tender"]

    appliesToLot: List[Lot] = None
    attachesTenderDocument: List[TenderDocument] = None
    tenderer: List[Agent] = None
    submittedDuring: TenderSubmission = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.appliesToLot:
            for appliesToLot in self.appliesToLot:
                g.add((self.uriRef, PUBC["appliesToLot"], appliesToLot.uriRef))

        if self.attachesTenderDocument:
            for attachesTenderDocument in self.attachesTenderDocument:
                g.add(
                    (self.uriRef, PUBC["attachesTenderDocument"], attachesTenderDocument.uriRef))

        if self.tenderer:
            for tenderer in self.tenderer:
                g.add((self.uriRef, PUBC["tenderer"], tenderer.uriRef))

        if self.submittedDuring:
            g.add((self.uriRef, PUBC["submittedDuring"],
                  self.submittedDuring.uriRef))
