from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from ..Thing import Thing


class Signposting(Characteristic):
    __type__ = PATHS["Signposting"]

    isSignpostingOf: List[Thing] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isSignpostingOf:
            for isSignpostingOf in self.isSignpostingOf:
                g.add(
                    (self.uriRef, PATHS["isSignpostingOf"], isSignpostingOf.uriRef))
