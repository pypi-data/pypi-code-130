from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .MonitoringFacility import MonitoringFacility

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Observation import Observation
    from .ObservationCollection import ObservationCollection


class Sensor(MonitoringFacility):
    __type__ = IOT["Sensor"]

    makesObservation: List[Observation] = None
    makesObservationCollection: List[ObservationCollection] = None
    description: List[Literal] = None
    identifier: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.makesObservation:
            for makesObservation in self.makesObservation:
                g.add(
                    (self.uriRef, IOT["makesObservation"], makesObservation.uriRef))

        if self.makesObservationCollection:
            for makesObservationCollection in self.makesObservationCollection:
                g.add(
                    (self.uriRef, IOT["makesObservationCollection"], makesObservationCollection.uriRef))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.identifier:
            g.add((self.uriRef, L0["identifier"], self.identifier))
