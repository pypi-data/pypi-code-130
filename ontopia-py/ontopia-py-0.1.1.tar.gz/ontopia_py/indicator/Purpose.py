from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Description import Description
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Indicator import Indicator


class Purpose(Description):
    __type__ = INDIC["Purpose"]

    isMetByIndicator: List[Indicator] = None
    name: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isMetByIndicator:
            for isMetByIndicator in self.isMetByIndicator:
                g.add(
                    (self.uriRef, INDIC["isMetByIndicator"], isMetByIndicator.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))
