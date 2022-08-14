from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .MeasurementUnit import MeasurementUnit
    from .Value import Value


class MeasureType(Characteristic):
    __type__ = MU["MeasureType"]

    hasMeasurementUnit: List[MeasurementUnit] = None
    isMeasureTypeOf: List(Value) = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasMeasurementUnit:
            for hasMeasurementUnit in self.hasMeasurementUnit:
                g.add((self.uriRef, MU["hasMeasurementUnit"],
                       hasMeasurementUnit.uriRef))

        if self.isMeasureTypeOf:
            for isMeasureTypeOf in self.isMeasureTypeOf:
                g.add((self.uriRef, MU["isMeasureTypeOf"],
                       isMeasureTypeOf.uriRef))
