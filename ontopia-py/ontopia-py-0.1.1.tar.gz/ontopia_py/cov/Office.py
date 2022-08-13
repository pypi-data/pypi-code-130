from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .SupportUnit import SupportUnit

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .eInvoiceService import eInvoiceService
    from .HomogeneousOrganizationalArea import HomogeneousOrganizationalArea


class Office(SupportUnit):
    __type__ = COV["Office"]

    hasEInvoiceService: eInvoiceService = None
    isPartOf: HomogeneousOrganizationalArea = None
    officeIdentifier: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasEInvoiceService:
            for hasEInvoiceService in self.hasEInvoiceService:
                g.add(
                    (self.uriRef, COV["hasEInvoiceService"], hasEInvoiceService.uriRef))

        if self.isPartOf:
            for isPartOf in self.isPartOf:
                g.add((self.uriRef, COV["isPartOf"], isPartOf.uriRef))

        if self.officeIdentifier:
            g.add((self.uriRef, COV["officeIdentifier"],
                  self.officeIdentifier))
