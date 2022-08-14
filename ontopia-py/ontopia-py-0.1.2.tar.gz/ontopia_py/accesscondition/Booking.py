from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .AccessCondition import AccessCondition

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class Booking(AccessCondition):
    __type__ = ACOND["Booking"]

    name: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isAccessConditionOf:
            for isAccessConditionOf in self.isAccessConditionOf:
                g.add((self.uriRef, ACOND["isAccessConditionOf"],
                       isAccessConditionOf.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))
