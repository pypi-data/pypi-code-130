from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Document import Document

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .WorkProgressReport import WorkProgressReport


class PaymentCertificate(Document):
    __type__ = PUBC["PaymentCertificate"]

    approvedInWPR: List[WorkProgressReport] = None
    paymentAmount: List[Literal] = None
    paymentCetificateDate: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.approvedInWPR:
            for approvedInWPR in self.approvedInWPR:
                g.add(
                    (self.uriRef, PUBC["approvedInWPR"], approvedInWPR.uriRef))

        if self.paymentAmount:
            for paymentAmount in self.paymentAmount:
                g.add((self.uriRef, PUBC["paymentAmount"], paymentAmount))

        if self.paymentCetificateDate:
            for paymentCetificateDate in self.paymentCetificateDate:
                g.add(
                    (self.uriRef, PUBC["paymentCetificateDate"], paymentCetificateDate))
