from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Activity import Activity
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .IndicatorCalculation import IndicatorCalculation


class CalculationMethod(Activity):
    __type__ = INDIC["CalculationMethod"]

    isCalculationMethodOf: List[IndicatorCalculation] = None
    name: List[Literal] = None
    description: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isCalculationMethodOf:
            for isCalculationMethodOf in self.isCalculationMethodOf:
                g.add(
                    (self.uriRef, INDIC["isCalculationMethodOf"], isCalculationMethodOf.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))
