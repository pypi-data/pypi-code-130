from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Entity import Entity
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from ..l0.Characteristic import Characteristic
    from ..Thing import Thing


class TemporalEntity(Entity):
    __type__ = TI["TemporalEntity"]

    hasTimeParameter: List[Characteristic] = []
    isTemporalEntityOf: List[Thing] = []

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        for hasTimeParameter in self.hasTimeParameter:
            g.add((self.uriRef, TI["hasTimeParameter"],
                  hasTimeParameter.uriRef))

        for isTemporalEntityOf in self.isTemporalEntityOf:
            g.add((self.uriRef, TI["isTemporalEntityOf"],
                  isTemporalEntityOf.uriRef))
