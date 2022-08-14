from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Observation import Observation
    from .ObservationValue import ObservationValue


class ObservationParameter(Characteristic):
    __type__ = IOT["ObservationParameter"]

    hasValueForObservationParameter: List[ObservationValue] = None
    isObservationParameterFor: List[Observation] = None
    name: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasValueForObservationParameter:
            for hasValueForObservationParameter in self.hasValueForObservationParameter:
                g.add((self.uriRef, IOT["hasValueForObservationParameter"],
                      hasValueForObservationParameter.uriRef))

        if self.isObservationParameterFor:
            for isObservationParameterFor in self.isObservationParameterFor:
                g.add(
                    (self.uriRef, IOT["isObservationParameterFor"], isObservationParameterFor.uriRef))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))
