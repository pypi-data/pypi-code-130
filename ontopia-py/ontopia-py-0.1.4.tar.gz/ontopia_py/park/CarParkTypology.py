from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Topic import Topic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .CarPark import CarPark


class CarParkTypology(Topic):
    __type__ = PARK["CarParkTypology"]

    isCarParkTypologyOf: List[CarPark] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isCarParkTypologyOf:
            for isCarParkTypologyOf in self.isCarParkTypologyOf:
                g.add(
                    (self.uriRef, PARK["isCarParkTypologyOf"], isCarParkTypologyOf.uriRef))
