from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Indicator import Indicator


class IndicatorType(Characteristic):
    __type__ = INDIC["IndicatorType"]

    isIndicatorTypeOf: List[Indicator] = None
    name: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isIndicatorTypeOf:
            for isIndicatorTypeOf in self.isIndicatorTypeOf:
                g.add(
                    (self.uriRef, INDIC["isIndicatorTypeOf"], isIndicatorTypeOf.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, l0["name"], name))
