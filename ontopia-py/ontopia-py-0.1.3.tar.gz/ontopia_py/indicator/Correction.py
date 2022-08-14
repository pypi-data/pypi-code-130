from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..l0.Activity import Activity
    from ..mu.Value import Value


class Correction(Characteristic):
    __type__ = INDIC["Correction"]

    isAppliedTo: List[Activity] = None
    hasCorrectionValue: Value = None
    doneAt: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isAppliedTo:
            for isAppliedTo in self.isAppliedTo:
                g.add((self.uriRef, INDIC["isAppliedTo"], isAppliedTo.uriRef))

        if self.hasCorrectionValue:
            g.add(
                (self.uriRef, INDIC["hasCorrectionValue"], self.hasCorrectionValue.uriRef))

        if self.doneAt:
            g.add((self.uriRef, INDIC["doneAt"], self.doneAt))
