from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.EventOrSituation import EventOrSituation
from ..ns import *
from ..poi.POINameInTime import POINameInTime

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..ti.TimeInterval import TimeInterval


class CISNameInTime(POINameInTime, EventOrSituation):
    __type__ = CIS["CISNameInTime"]

    isValidDuring: List[TimeInterval] = None
    institutionalCISName: List[Literal] = None
    altCISName: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isValidDuring:
            for isValidDuring in self.isValidDuring:
                g.add(
                    (self.uriRef, CIS["isValidDuring"], isValidDuring.uriRef))

        if self.institutionalCISName:
            for institutionalCISName in self.institutionalCISName:
                g.add(
                    (self.uriRef, CIS["institutionalCISName"], institutionalCISName))

        if self.altCISName:
            for altCISName in self.altCISName:
                g.add((self.uriRef, CIS["altCISName"], altCISName))
