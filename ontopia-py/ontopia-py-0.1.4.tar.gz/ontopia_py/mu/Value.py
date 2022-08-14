from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .MeasurementUnit import MeasurementUnit
    from .MeasureType import MeasureType


class Value(Characteristic):
    __type__ = MU["Value"]

    hasMeasurementUnit: List[MeasurementUnit] = None
    hasMeasureType: MeasureType = None
    value: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasMeasurementUnit:
            for hasMeasurementUnit in self.hasMeasurementUnit:
                g.add((self.uriRef, MU["hasMeasurementUnit"],
                       hasMeasurementUnit.uriRef))

        if self.hasMeasureType:
            g.add((self.uriRef, MU["hasMeasureType"],
                  self.hasMeasureType.uriRef))

        if self.value:
            for value in self.value:
                g.add((self.uriRef, MU["value"], value))
