from __future__ import annotations

from typing import TYPE_CHECKING, List

from rdflib import URIRef

from ..ns import *
from .TemporalEntity import TemporalEntity

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..Thing import Thing


class MonthOfYear(TemporalEntity):
    __type__ = TI["MonthOfYear"]

    isMonthOfYearOf: List[Thing] = []
    month: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        for isMonthOfYearOf in self.isMonthOfYearOf:
            g.add((self.uriRef, TI["isMonthOfYearOf"],
                  isMonthOfYearOf.uriRef))

        if self.month:
            g.add((self.uriRef, TI["month"], self.month))


class January(MonthOfYear):
    def __init__(self):
        self.uriRef = URIRef(TI["January"])


class February(MonthOfYear):
    def __init__(self):
        self.uriRef = URIRef(TI["February"])


class March(MonthOfYear):
    def __init__(self):
        self.uriRef = URIRef(TI["March"])


class April(MonthOfYear):
    def __init__(self):
        self.uriRef = URIRef(TI["April"])


class May(MonthOfYear):
    def __init__(self):
        self.uriRef = URIRef(TI["May"])


class June(MonthOfYear):
    def __init__(self):
        self.uriRef = URIRef(TI["June"])


class July(MonthOfYear):
    def __init__(self):
        self.uriRef = URIRef(TI["July"])


class August(MonthOfYear):
    def __init__(self):
        self.uriRef = URIRef(TI["August"])


class September(MonthOfYear):
    def __init__(self):
        self.uriRef = URIRef(TI["September"])


class October(MonthOfYear):
    def __init__(self):
        self.uriRef = URIRef(TI["October"])


class November(MonthOfYear):
    def __init__(self):
        self.uriRef = URIRef(TI["November"])


class December(MonthOfYear):
    def __init__(self):
        self.uriRef = URIRef(TI["December"])
