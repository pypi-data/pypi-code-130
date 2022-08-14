from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .MonitoringFacility import MonitoringFacility


class Platform(Object):
    __type__ = IOT["Platform"]

    hostsMonitoringFacility: List[MonitoringFacility] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hostsMonitoringFacility:
            for hostsMonitoringFacility in self.hostsMonitoringFacility:
                g.add(
                    (self.uriRef, IOT["hostsMonitoringFacility"], hostsMonitoringFacility.uriRef))
