from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..cpev.PublicEvent import PublicEvent
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .CulturalEntity import CulturalEntity
    from .Site import Site


class CulturalEvent(PublicEvent):
    __type__ = CIS["CulturalEvent"]

    isHostedBySite: List[Site] = None
    involvesCulturalEntity: List[CulturalEntity] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isHostedBySite:
            for isHostedBySite in self.isHostedBySite:
                g.add(
                    (self.uriRef, CIS["isHostedBySite"], isHostedBySite.uriRef))

        if self.involvesCulturalEntity:
            for involvesCulturalEntity in self.involvesCulturalEntity:
                g.add(
                    (self.uriRef, CIS["involvesCulturalEntity"], involvesCulturalEntity.uriRef))
