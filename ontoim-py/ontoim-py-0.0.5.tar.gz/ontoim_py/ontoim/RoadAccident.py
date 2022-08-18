from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.l0.EventOrSituation import EventOrSituation

from ..ns import *

if TYPE_CHECKING:
    from ontopia_py.clv.Geometry import Geometry
    from rdflib import Graph, Literal

    from .AccidentType import AccidentType
    from .InvolvedEntity import InvolvedEntity
    from .InvolvedObstacle import InvolvedObstacle
    from .InvolvedPerson import InvolvedPerson
    from .InvolvedVehicle import InvolvedVehicle
    from .RevelationUnit import RevelationUnit
    from .Road import Road
    from .WeatherCondition import WeatherCondition


class RoadAccident(EventOrSituation):
    __type__ = ONTOIM["RoadAccident"]

    detectedBy: List[RevelationUnit] = None
    hasInvolvedEntity: List[InvolvedEntity] = None
    hasInvolvedObstacle: List[InvolvedObstacle] = None
    hasInvolvedPerson: List[InvolvedPerson] = None
    hasInvolvedVehicle: List[InvolvedVehicle] = None
    hasWeatherCondition: List[WeatherCondition] = None
    hasGeometry: Geometry
    hasAccidentType: AccidentType = None
    hasRoad: Road = None
    date: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.detectedBy:
            for detectedBy in self.detectedBy:
                g.add((self.uriRef, ONTOIM["detectedBy"], detectedBy.uriRef))

        if self.hasInvolvedEntity:
            for hasInvolvedEntity in self.hasInvolvedEntity:
                g.add(
                    (self.uriRef, ONTOIM["hasInvolvedEntity"], hasInvolvedEntity.uriRef))

        if self.hasInvolvedObstacle:
            for hasInvolvedObstacle in self.hasInvolvedObstacle:
                g.add(
                    (self.uriRef, ONTOIM["hasInvolvedObstacle"], hasInvolvedObstacle.uriRef))

        if self.hasInvolvedPerson:
            for hasInvolvedPerson in self.hasInvolvedPerson:
                g.add(
                    (self.uriRef, ONTOIM["hasInvolvedPerson"], hasInvolvedPerson.uriRef))

        if self.hasInvolvedVehicle:
            for hasInvolvedVehicle in self.hasInvolvedVehicle:
                g.add(
                    (self.uriRef, ONTOIM["hasInvolvedVehicle"], hasInvolvedVehicle.uriRef))

        if self.hasWeatherCondition:
            for hasWeatherCondition in self.hasWeatherCondition:
                g.add(
                    (self.uriRef, ONTOIM["hasWeatherCondition"], hasWeatherCondition.uriRef))

        if self.hasGeometry:
            g.add((self.uriRef, ONTOIM["hasGeometry"],
                  self.hasGeometry.uriRef))

        if self.hasAccidentType:
            g.add((self.uriRef, ONTOIM["hasAccidentType"],
                  self.hasAccidentType.uriRef))

        if self.hasRoad:
            g.add((self.uriRef, ONTOIM["hasRoad"],
                  self.hasRoad.uriRef))

        if self.date:
            g.add((self.uriRef, TI["date"], self.date))
