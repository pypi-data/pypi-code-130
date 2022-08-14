from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from ..l0.Characteristic import Characteristic

if TYPE_CHECKING:
    from rdflib import Graph

    from .MeasurementQualityValue import MeasurementQualityValue


class MeasurementQuality(Characteristic):
    __type__ = IOT["MeasurementQuality"]

    hasMeasurementQualityValue: List[MeasurementQualityValue] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasMeasurementQualityValue:
            for hasMeasurementQualityValue in self.hasMeasurementQualityValue:
                g.add(
                    (self.uriRef, IOT["hasMeasurementQualityValue"], hasMeasurementQualityValue.uriRef))
