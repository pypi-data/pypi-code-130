from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Description import Description
from ..l0.Sequence import Sequence
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..clv.Geometry import Geometry
    from ..clv.SpatialObject import SpatialObject
    from ..mu.Value import Value
    from ..Thing import Thing
    from .RouteType import RouteType
    from .Stage import Stage


class Route(Description, Sequence):
    __type__ = ROUTE["Route"]

    hasLength: List[Value] = None
    hasMember: List[Stage] = None
    crosses: List[SpatialObject] = None
    isDeviationOf: List[Thing] = None
    isPrefRouteOf: List[Thing] = None
    isRouteOf: List[Thing] = None
    hasGeometry: Geometry = None
    hasRouteType: RouteType = None
    routeLongName: List[Literal] = None
    routeShortName: List[Literal] = None
    routelLength: List[Literal] = None
    description: List[Literal] = None
    routeEstDuration: List[Literal] = None
    numberOfStages: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasLength:
            for hasLength in self.hasLength:
                g.add((self.uriRef, ROUTE["hasLength"], hasLength.uriRef))

        if self.hasMember:
            for hasMember in self.hasMember:
                g.add((self.uriRef, L0["hasMember"], hasMember.uriRef))

        if self.crosses:
            for crosses in self.crosses:
                g.add((self.uriRef, ROUTE["crosses"], crosses.uriRef))

        if self.isDeviationOf:
            for isDeviationOf in self.isDeviationOf:
                g.add(
                    (self.uriRef, ROUTE["isDeviationOf"], isDeviationOf.uriRef))

        if self.isPrefRouteOf:
            for isPrefRouteOf in self.isPrefRouteOf:
                g.add(
                    (self.uriRef, ROUTE["isPrefRouteOf"], isPrefRouteOf.uriRef))

        if self.isRouteOf:
            for isRouteOf in self.isRouteOf:
                g.add((self.uriRef, ROUTE["isRouteOf"], isRouteOf.uriRef))

        if self.hasGeometry:
            g.add((self.uriRef, CLV["hasGeometry"], self.hasGeometry.uriRef))

        if self.hasRouteType:
            g.add((self.uriRef, ROUTE["hasRouteType"],
                  self.hasRouteType.uriRef))

        if self.routeLongName:
            for routeLongName in self.routeLongName:
                g.add((self.uriRef, ROUTE["routeLongName"], routeLongName))

        if self.routeShortName:
            for routeShortName in self.routeShortName:
                g.add((self.uriRef, ROUTE["routeShortName"], routeShortName))

        if self.routelLength:
            for routelLength in self.routelLength:
                g.add((self.uriRef, ROUTE["routelLength"], routelLength))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.routeEstDuration:
            for routeEstDuration in self.routeEstDuration:
                g.add(
                    (self.uriRef, ROUTE["routeEstDuration"], routeEstDuration))

        if self.numberOfStages:
            g.add((self.uriRef, ROUTE["numberOfStages"], self.numberOfStages))
