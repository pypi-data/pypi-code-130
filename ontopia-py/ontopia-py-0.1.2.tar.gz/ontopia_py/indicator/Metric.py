from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .IndicatorCalculation import IndicatorCalculation
    from .Parameter import Parameter


class Metric(Characteristic):
    __type__ = INDIC["Metric"]

    isMetricOf: List[IndicatorCalculation] = None
    hasParameter: List[Parameter] = None
    description: List[Literal] = None
    description: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isMetricOf:
            for isMetricOf in self.isMetricOf:
                g.add(
                    (self.uriRef, INDIC["isMetricOf"], isMetricOf.uriRef))

        if self.hasParameter:
            for hasParameter in self.hasParameter:
                g.add(
                    (self.uriRef, INDIC["hasParameter"], hasParameter.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))
