from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .TemporalEntity import TemporalEntity

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..Thing import Thing


class Year(TemporalEntity):
    __type__ = TI["Year"]

    year: Literal = None
    isYearOf: List[Thing] = []

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        for isYearOf in self.isYearOf:
            g.add((self.uriRef, TI["isYearOf"], isYearOf.uriRef))

        if self.year:
            g.add((self.uriRef, TI["year"], self.year))
