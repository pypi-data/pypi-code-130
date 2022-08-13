from __future__ import annotations

from typing import TYPE_CHECKING

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class eInvoiceService(Object):
    __type__ = COV["eInvoiceService"]

    eInvoiceServiceStartingDate: Literal = None
    taxCodeEInvoiceService: Literal = None
    taxCodeValidationDate: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.eInvoiceServiceStartingDate:
            g.add((self.uriRef, COV["eInvoiceServiceStartingDate"],
                  self.eInvoiceServiceStartingDate))

        if self.taxCodeEInvoiceService:
            g.add((self.uriRef, COV["taxCodeEInvoiceService"],
                  self.taxCodeEInvoiceService))

        if self.taxCodeValidationDate:
            g.add((self.uriRef, COV["taxCodeValidationDate"],
                  self.taxCodeValidationDate))
