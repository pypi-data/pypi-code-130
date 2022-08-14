from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Entity import Entity
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..iot.Observation import Observation
    from .IndicatorCalculation import IndicatorCalculation


class Address(Entity):
    __type__ = INDIC["Address"]

    isDatumSourceOf: List[IndicatorCalculation] = None
    isProvidedBy: List[Observation] = None
    name: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isDatumSourceOf:
            for isDatumSourceOf in self.isDatumSourceOf:
                g.add(
                    (self.uriRef, INDIC["isDatumSourceOf"], isDatumSourceOf.uriRef))

        if self.isProvidedBy:
            for isProvidedBy in self.isProvidedBy:
                g.add(
                    (self.uriRef, INDIC["isProvidedBy"], isProvidedBy.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))
