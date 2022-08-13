from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.EventOrSituation import EventOrSituation
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .EventType import EventType
    from .PublicService import PublicService


class EventOrSituation(EventOrSituation):
    __type__ = CPSV["EventOrSituation"]

    hasEventType: List[EventType] = None
    isEventForPS: List[PublicService] = None
    name: List[Literal] = None
    description: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasEventType:
            for hasEventType in self.hasEventType:
                g.add((self.uriRef, CPSV["hasEventType"], hasEventType.uriRef))

        if self.isEventForPS:
            for isEventForPS in self.isEventForPS:
                g.add((self.uriRef, CPSV["isEventForPS"], isEventForPS.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))
