from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..sm.OnlineContactPoint import OnlineContactPoint
    from .CulturalInstituteOrSite import CulturalInstituteOrSite


class CISService(Characteristic):
    __type__ = CIS["CISService"]

    isProvidedBy: List[CulturalInstituteOrSite] = None
    hasOnlineContactPoint: List[OnlineContactPoint] = None
    name: List[Literal] = None
    description: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isProvidedBy:
            for isProvidedBy in self.isProvidedBy:
                g.add(
                    (self.uriRef, CIS["isProvidedBy"], isProvidedBy.uriRef))

        if self.hasOnlineContactPoint:
            for hasOnlineContactPoint in self.hasOnlineContactPoint:
                g.add(
                    (self.uriRef, SM["hasOnlineContactPoint"], hasOnlineContactPoint.uriRef))

        if self.name:
            for name in self.name:
                g.add(
                    (self.uriRef, L0["name"], name))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))
