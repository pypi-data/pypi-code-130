from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .Document import Document

if TYPE_CHECKING:
    from rdflib import Graph

    from .Tender import Tender


class TenderDocument(Document):
    __type__ = PUBC["TenderDocument"]

    refersToTender: Tender = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.refersToTender:
            g.add((self.uriRef, PUBC["refersToTender"],
                  self.refersToTender.uriRef))
