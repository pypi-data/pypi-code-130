from __future__ import annotations

from typing import TYPE_CHECKING, List, Union

from ..l0.Collection import Collection
from ..ns import *
from .CulturalEntity import CulturalEntity

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..ti.TimeInterval import TimeInterval
    from .Catalogue import Catalogue
    from .CollectionCulEnt import CollectionCulEnt
    from .CulturalHeritageObject import CulturalHeritageObject


class CollectionCulEnt(CulturalEntity, Collection):
    __type__ = CIS["CollectionCulEnt"]

    hasMemberColCultEnt: List[Union[CollectionCulEnt,
                                    CulturalHeritageObject]] = None
    isDescribedBy: List[Catalogue] = None
    atTime: List[TimeInterval] = None
    name: List[Literal] = None
    description: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasMemberColCultEnt:
            for hasMemberColCultEnt in self.hasMemberColCultEnt:
                g.add(
                    (self.uriRef, CIS["hasMemberColCultEnt"], hasMemberColCultEnt.uriRef))

        if self.isDescribedBy:
            for isDescribedBy in self.isDescribedBy:
                g.add(
                    (self.uriRef, CIS["isDescribedBy"], isDescribedBy.uriRef))

        if self.atTime:
            for atTime in self.atTime:
                g.add((self.uriRef, TI["atTime"], atTime.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))
