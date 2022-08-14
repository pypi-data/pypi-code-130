from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Collection import Collection
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Observation import Observation
    from .Sensor import Sensor


class ObservationCollection(Collection):
    __type__ = IOT["ObservationCollection"]

    consistsOf: List[Observation] = None
    observationCollectionMadeBySensor: Sensor = None
    identifier: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.consistsOf:
            for consistsOf in self.consistsOf:
                g.add((self.uriRef, IOT["consistsOf"], consistsOf.uriRef))

        if self.observationCollectionMadeBySensor:
            g.add((self.uriRef, IOT["observationCollectionMadeBySensor"],
                  self.observationCollectionMadeBySensor.uriRef))

        if self.identifier:
            g.add((self.uriRef, L0["identifier"], self.identifier))
