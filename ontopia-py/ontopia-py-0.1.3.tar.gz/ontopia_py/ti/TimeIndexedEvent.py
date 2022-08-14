from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.EventOrSituation import EventOrSituation
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .TimeInterval import TimeInterval


class TimeIndexedEvent(EventOrSituation):
    __type__ = TI["TimeIndexedEvent"]

    atTime: List[TimeInterval] = []

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        for atTime in self.atTime:
            g.add((self.uriRef, TI["atTime"], atTime.uriRef))
