from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Activity import Activity
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..clv.Geometry import Geometry
    from ..ti.TimeInterval import TimeInterval
    from .FeatureOfInterest import FeatureOfInterest
    from .MeasurementQuality import MeasurementQuality
    from .Method import Method
    from .ObservationCollection import ObservationCollection
    from .ObservationParameter import ObservationParameter
    from .ObservationValue import ObservationValue
    from .Platform import Platform
    from .Sensor import Sensor


class Observation(Activity):
    __type__ = IOT["Observation"]

    hasObservationParameter: List[ObservationParameter] = None
    hasObservationValue: List[ObservationValue] = None
    hasQuality: List[MeasurementQuality] = None
    usedMethod: List[Method] = None
    comesFrom: List[Platform] = None
    hasFeatureOfInterest: FeatureOfInterest = None
    isPartOf: ObservationCollection = None
    observationMadeBySensor: Sensor = None
    hasGeometry: Geometry = None
    generationTime: TimeInterval = None
    phenomenonTime: TimeInterval = None
    atTime: TimeInterval = None
    description: List[Literal] = None
    identifier: Literal = None
    issued: Literal = None
    modified: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasObservationParameter:
            for hasObservationParameter in self.hasObservationParameter:
                g.add(
                    (self.uriRef, IOT["hasObservationParameter"], hasObservationParameter.uriRef))

        if self.hasObservationValue:
            for hasObservationValue in self.hasObservationValue:
                g.add(
                    (self.uriRef, IOT["hasObservationValue"], hasObservationValue.uriRef))

        if self.hasQuality:
            for hasQuality in self.hasQuality:
                g.add((self.uriRef, IOT["hasQuality"], hasQuality.uriRef))

        if self.usedMethod:
            for usedMethod in self.usedMethod:
                g.add((self.uriRef, IOT["usedMethod"], usedMethod.uriRef))

        if self.comesFrom:
            for comesFrom in self.comesFrom:
                g.add((self.uriRef, IOT["comesFrom"], comesFrom.uriRef))

        if self.hasFeatureOfInterest:
            g.add((self.uriRef, IOT["hasFeatureOfInterest"],
                  self.hasFeatureOfInterest.uriRef))

        if self.isPartOf:
            g.add((self.uriRef, IOT["isPartOf"], self.isPartOf.uriRef))

        if self.observationMadeBySensor:
            g.add((self.uriRef, IOT["observationMadeBySensor"],
                  self.observationMadeBySensor.uriRef))

        if self.hasGeometry:
            g.add((self.uriRef, CLV["hasGeometry"], self.hasGeometry.uriRef))

        if self.generationTime:
            g.add((self.uriRef, IOT["generationTime"],
                  self.generationTime.uriRef))

        if self.phenomenonTime:
            g.add((self.uriRef, IOT["phenomenonTime"],
                  self.phenomenonTime.uriRef))

        if self.atTime:
            g.add((self.uriRef, TI["atTime"], self.atTime.uriRef))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.identifier:
            g.add((self.uriRef, L0["identifier"], self.identifier))

        if self.issued:
            g.add((self.uriRef, TI["issued"], self.issued))

        if self.modified:
            g.add((self.uriRef, TI["modified"], self.modified))
