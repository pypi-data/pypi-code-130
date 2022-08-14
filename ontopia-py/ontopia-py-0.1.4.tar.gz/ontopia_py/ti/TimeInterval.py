from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .TemporalEntity import TemporalEntity

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .TimeInstant import TimeInstant


class TimeInterval(TemporalEntity):
    __type__ = TI["TimeInterval"]

    hasTimeInstantInside: List[TimeInstant] = []
    date: List[Literal] = []
    endTime: Literal = None
    startTime: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        for hasTimeInstantInside in self.hasTimeInstantInside:
            g.add((self.uriRef, TI["hasTimeInstantInside"],
                  hasTimeInstantInside.uriRef))

        for date in self.date:
            g.add((self.uriRef, TI["date"], date.uriRef))

        if self.endTime:
            g.add((self.uriRef, TI["endTime"], self.endTime))

        if self.startTime:
            g.add((self.uriRef, TI["startTime"], self.startTime))
