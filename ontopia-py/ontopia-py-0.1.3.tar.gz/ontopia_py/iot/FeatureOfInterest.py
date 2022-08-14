from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from ..l0.Entity import Entity

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Observation import Observation


class FeatureOfInterest(Entity):
    __type__ = IOT["FeatureOfInterest"]

    isFeatureOfInterestFor: List[Observation] = None
    name: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isFeatureOfInterestFor:
            for isFeatureOfInterestFor in self.isFeatureOfInterestFor:
                g.add(
                    (self.uriRef, IOT["isFeatureOfInterestFor"], isFeatureOfInterestFor.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))
