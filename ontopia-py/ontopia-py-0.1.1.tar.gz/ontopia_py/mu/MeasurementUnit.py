from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from ..Thing import Thing


class MeasurementUnit(Characteristic):
    __type__ = MU["MeasurementUnit"]

    isMeasurementUnitOf: List[Thing] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isMeasurementUnitOf:
            for isMeasurementUnitOf in self.isMeasurementUnitOf:
                g.add((self.uriRef, MU["isMeasurementUnitOf"],
                       isMeasurementUnitOf.uriRef))
