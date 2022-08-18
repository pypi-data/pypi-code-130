from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.poi.PointOfInterest import PointOfInterest

from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .PlantStatusInTime import PlantStatusInTime


class Plant(PointOfInterest):
    __type__ = ONTOIM["Plant"]

    hasStatusInTime: List[PlantStatusInTime] = None
    commonName: List[Literal] = None
    plantCode: Literal = None
    species: Literal = None
    birthYear: Literal = None
    plantingDate: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasStatusInTime:
            for hasStatusInTime in self.hasStatusInTime:
                g.add(
                    (self.uriRef, ONTOIM["hasStatusInTime"], hasStatusInTime.uriRef))

        if self.commonName:
            for commonName in self.commonName:
                g.add((self.uriRef, ONTOIM["commonName"], commonName))

        if self.plantCode:
            g.add((self.uriRef, ONTOIM["plantCode"], self.plantCode))

        if self.species:
            g.add((self.uriRef, ONTOIM["species"], self.species))

        if self.birthYear:
            g.add((self.uriRef, ONTOIM["birthYear"], self.birthYear))

        if self.plantingDate:
            g.add((self.uriRef, ONTOIM["plantingDate"], self.plantingDate))
