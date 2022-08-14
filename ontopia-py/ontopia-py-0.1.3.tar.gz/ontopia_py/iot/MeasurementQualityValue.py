from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from ..mu.Value import Value

if TYPE_CHECKING:
    from rdflib import Graph

    from .MeasurementQuality import MeasurementQuality


class MeasurementQualityValue(Value):
    __type__ = IOT["MeasurementQualityValue"]

    isMeasurementQualityValueOf: List[MeasurementQuality] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isMeasurementQualityValueOf:
            for isMeasurementQualityValueOf in self.isMeasurementQualityValueOf:
                g.add(
                    (self.uriRef, IOT["isMeasurementQualityValueOf"], isMeasurementQualityValueOf.uriRef))
