from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Entity import Entity
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .CulturalEvent import CulturalEvent


class CulturalEntity(Entity):
    __type__ = CIS["CulturalEntity"]

    isInvolvedInCulturalEvent: List[CulturalEvent] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isInvolvedInCulturalEvent:
            for isInvolvedInCulturalEvent in self.isInvolvedInCulturalEvent:
                g.add(
                    (self.uriRef, CIS["isInvolvedInCulturalEvent"], isInvolvedInCulturalEvent.uriRef))
