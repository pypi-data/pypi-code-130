from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *
from .CulturalEntity import CulturalEntity

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Site import Site


class CulturalHeritageObject(CulturalEntity, Object):
    __type__ = CIS["CulturalHeritageObject"]

    isInSite: List[Site] = None
    name: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isInSite:
            for isInSite in self.isInSite:
                g.add((self.uriRef, CIS["isInSite"], isInSite.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))
