from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .ProcurementDocument import ProcurementDocument

if TYPE_CHECKING:
    from rdflib import Graph

    from .CommonProcurementVocabulary import CommonProcurementVocabulary
    from .NoticeType import NoticeType


class Notice(ProcurementDocument):
    __type__ = PUBC["Notice"]

    hasCPV: List[CommonProcurementVocabulary] = None
    hasNoticeType: NoticeType = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasCPV:
            for hasCPV in self.hasCPV:
                g.add((self.uriRef, PUBC["hasCPV"], hasCPV.uriRef))

        if self.hasNoticeType:
            g.add((self.uriRef, PUBC["hasNoticeType"],
                  self.hasNoticeType.uriRef))
