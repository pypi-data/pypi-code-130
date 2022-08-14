from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .AmendmentDocument import AmendmentDocument

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .SuspensionReason import SuspensionReason


class SuspensionDocument(AmendmentDocument):
    __type__ = PUBC["SuspensionDocument"]

    suspensionReason: List[SuspensionReason] = None
    resumptionDate: List[Literal] = None
    suspensionDate: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.suspensionReason:
            for suspensionReason in self.suspensionReason:
                g.add(
                    (self.uriRef, PUBC["suspensionReason"], suspensionReason.uriRef))

        if self.resumptionDate:
            for resumptionDate in self.resumptionDate:
                g.add((self.uriRef, PUBC["resumptionDate"], resumptionDate))

        if self.suspensionDate:
            for suspensionDate in self.suspensionDate:
                g.add((self.uriRef, PUBC["suspensionDate"], suspensionDate))
