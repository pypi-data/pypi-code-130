from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Topic import Topic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .PublicEvent import PublicEvent


class PublicEventTypology(Topic):
    __type__ = CPEV["PublicEventTypology"]

    isPublicEventTypologyOf: List[PublicEvent] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isPublicEventTypologyOf:
            for isPublicEventTypologyOf in self.isPublicEventTypologyOf:
                g.add(
                    (self.uriRef, CPEV["isPublicEventTypologyOf"], isPublicEventTypologyOf.uriRef))
