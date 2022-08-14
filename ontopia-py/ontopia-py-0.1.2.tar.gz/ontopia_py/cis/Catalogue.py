from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..sm.WebSite import WebSite
    from .CollectionCulEnt import CollectionCulEnt
    from .CulturalInstituteOrSite import CulturalInstituteOrSite


class Catalogue(Object):
    __type__ = CIS["Catalogue"]

    describesCulturalEntity: List[CollectionCulEnt] = None
    isCatalogueOf: List[CulturalInstituteOrSite] = None
    hasWebSite: List[WebSite] = None
    name: List[Literal] = None
    description: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.describesCulturalEntity:
            for describesCulturalEntity in self.describesCulturalEntity:
                g.add(
                    (self.uriRef, CIS["describesCulturalEntity"], describesCulturalEntity.uriRef))

        if self.isCatalogueOf:
            for isCatalogueOf in self.isCatalogueOf:
                g.add(
                    (self.uriRef, CIS["isCatalogueOf"], isCatalogueOf.uriRef))

        if self.hasWebSite:
            for hasWebSite in self.hasWebSite:
                g.add((self.uriRef, SM["hasWebSite"], hasWebSite.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))
