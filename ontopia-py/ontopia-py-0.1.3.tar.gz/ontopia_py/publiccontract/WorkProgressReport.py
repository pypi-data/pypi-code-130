from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Document import Document

if TYPE_CHECKING:
    from rdflib import Graph

    from .PaymentCertificate import PaymentCertificate


class VariantDocument(Document):
    __type__ = PUBC["VariantDocument"]

    containsPaymentCertificate: List[PaymentCertificate] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.containsPaymentCertificate:
            for containsPaymentCertificate in self.containsPaymentCertificate:
                g.add(
                    (self.uriRef, PUBC["containsPaymentCertificate"], containsPaymentCertificate.uriRef))
