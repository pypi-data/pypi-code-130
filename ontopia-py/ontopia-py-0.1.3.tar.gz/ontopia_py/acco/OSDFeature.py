from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class OSDFeature(Characteristic):
    __type__ = ACCO["OSDFeature"]

    featureName: List[Literal] = None
    featureDescription: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.featureName:
            for featureName in self.featureName:
                g.add((self.uriRef, ACCO["featureName"], featureName))

        if self.featureDescription:
            for featureDescription in self.featureDescription:
                g.add(
                    (self.uriRef, ACCO["featureDescription"], featureDescription))
