from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from ..mu.Value import Value

if TYPE_CHECKING:
    from rdflib import Graph

    from .Observation import Observation
    from .ObservationParameter import ObservationParameter


class ObservationValue(Value):
    __type__ = IOT["ObservationValue"]

    isObservationValueOf: List[Observation] = None
    isValueForObservationParameter: List[ObservationParameter] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isObservationValueOf:
            for isObservationValueOf in self.isObservationValueOf:
                g.add(
                    (self.uriRef, IOT["isObservationValueOf"], isObservationValueOf.uriRef))

        if self.isValueForObservationParameter:
            for isValueForObservationParameter in self.isValueForObservationParameter:
                g.add(
                    (self.uriRef, IOT["isValueForObservationParameter"], isValueForObservationParameter.uriRef))
