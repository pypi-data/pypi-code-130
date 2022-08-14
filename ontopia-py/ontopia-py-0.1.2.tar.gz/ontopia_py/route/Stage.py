from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *
from ..poi.MultiplePointOfInterest import MultiplePointOfInterest

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class Stage(MultiplePointOfInterest, Object):
    __type__ = ROUTE["Stage"]

    directlyFollows: List[Stage] = None
    directlyPrecedes: List[Stage] = None
    follows: List[Stage] = None
    precedes: List[Stage] = None
    stageOrdering: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.directlyFollows:
            for directlyFollows in self.directlyFollows:
                g.add(
                    (self.uriRef, L0["directlyFollows"], directlyFollows.uriRef))

        if self.directlyPrecedes:
            for directlyPrecedes in self.directlyPrecedes:
                g.add(
                    (self.uriRef, L0["directlyPrecedes"], directlyPrecedes.uriRef))

        if self.follows:
            for follows in self.follows:
                g.add((self.uriRef, L0["follows"], follows.uriRef))

        if self.precedes:
            for precedes in self.precedes:
                g.add((self.uriRef, L0["precedes"], precedes.uriRef))

        if self.stageOrdering:
            g.add((self.uriRef, ROUTE["stageOrdering"], self.stageOrdering))
