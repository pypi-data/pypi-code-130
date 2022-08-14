from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .AccessCondition import AccessCondition

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..ti.DayOfWeek import DayOfWeek
    from ..ti.TimeInterval import TimeInterval


class TemporaryClosure(AccessCondition):
    __type__ = ACOND["TemporaryClosure"]

    atTime: List[TimeInterval] = None
    hasDayOfWeek: List[DayOfWeek] = None
    reasonClosure: List[Literal] = None
    closes: List[Literal] = None
    opens: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.atTime:
            for atTime in self.atTime:
                g.add((self.uriRef, TI["atTime"], atTime.uriRef))

        if self.hasDayOfWeek:
            for hasDayOfWeek in self.hasDayOfWeek:
                g.add((self.uriRef, TI["hasDayOfWeek"], hasDayOfWeek.uriRef))

        if self.reasonClosure:
            for reasonClosure in self.reasonClosure:
                g.add((self.uriRef, ACOND["reasonClosure"], reasonClosure))

        if self.closes:
            for closes in self.closes:
                g.add((self.uriRef, ACOND["closes"], closes))

        if self.opens:
            for opens in self.opens:
                g.add((self.uriRef, ACOND["opens"], opens))
