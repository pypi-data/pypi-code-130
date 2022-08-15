from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.iot.TrafficFlow import TrafficFlow

from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .TrafficFlowDirection import TrafficFlowDirection
    from .VehicleCategory import VehicleCategory


class TrafficFlow(TrafficFlow):
    __type__ = ONTOIM["TrafficFlow"]

    hasTrafficFlowDirection: TrafficFlowDirection = None
    hasVehicleCategory: List[VehicleCategory] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasTrafficFlowDirection:
            g.add((self.uriRef, ONTOIM["hasTrafficFlowDirection"],
                  self.hasTrafficFlowDirection.uriRef))

        if self.hasVehicleCategory:
            for hasVehicleCategory in self.hasVehicleCategory:
                g.add(
                    (self.uriRef, ONTOIM["hasVehicleCategory"], hasVehicleCategory.uriRef))
