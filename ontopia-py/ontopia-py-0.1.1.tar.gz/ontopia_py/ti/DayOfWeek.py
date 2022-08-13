from __future__ import annotations

from typing import TYPE_CHECKING, List

from rdflib import URIRef

from ..ns import *
from .TemporalEntity import TemporalEntity

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..Thing import Thing


class DayOfWeek(TemporalEntity):
    __type__ = TI["DayOfWeek"]

    isDayOfWeekOf: List[Thing] = []
    day: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        for isDayOfWeekOf in self.isDayOfWeekOf:
            g.add((self.uriRef, TI["isDayOfWeekOf"],
                  isDayOfWeekOf.uriRef))

        if self.day:
            g.add((self.uriRef, TI["day"], self.day))


class Monday(DayOfWeek):
    def __init__(self):
        self.uriRef = URIRef(TI["Monday"])


class Tuesday(DayOfWeek):
    def __init__(self):
        self.uriRef = URIRef(TI["Tuesday"])


class Wednesday(DayOfWeek):
    def __init__(self):
        self.uriRef = URIRef(TI["Wednesday"])


class Thursday(DayOfWeek):
    def __init__(self):
        self.uriRef = URIRef(TI["Thursday"])


class Friday(DayOfWeek):
    def __init__(self):
        self.uriRef = URIRef(TI["Friday"])


class Saturday(DayOfWeek):
    def __init__(self):
        self.uriRef = URIRef(TI["Saturday"])


class Sunday(DayOfWeek):
    def __init__(self):
        self.uriRef = URIRef(TI["Sunday"])
