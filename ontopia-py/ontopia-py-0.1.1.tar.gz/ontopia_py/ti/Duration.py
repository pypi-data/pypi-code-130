from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .TimeInterval import TimeInterval

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..Thing import Thing


class Duration(TimeInterval):
    __type__ = TI["Duration"]

    isDurationOf: List[Thing] = []
    duration: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        for isDurationOf in self.isDurationOf:
            g.add((self.uriRef, TI["isDurationOf"],
                  isDurationOf.uriRef))

        if self.duration:
            g.add((self.uriRef, TI["duration"], self.duration))
