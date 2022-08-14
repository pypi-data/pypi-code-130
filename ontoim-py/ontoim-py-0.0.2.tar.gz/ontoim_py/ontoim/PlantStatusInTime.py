from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.l0.EventOrSituation import EventOrSituation

from ..ns import *

if TYPE_CHECKING:
    from ontopia_py.mu.Value import Value
    from ontopia_py.ti.TemporalEntity import TemporalEntity
    from rdflib import Graph

    from .PlantHealthStatus import PlantHealthStatus


class PlantStatusInTime(EventOrSituation):
    __type__ = ONTOIM["PlantStatusInTime"]

    hasDiameter: List[Value] = None
    hasHeight: List[Value] = None
    hasTemporalEntity: TemporalEntity = None
    hasHealthStatus: PlantHealthStatus = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasDiameter:
            for hasDiameter in self.hasDiameter:
                g.add((self.uriRef, ONTOIM["hasDiameter"], hasDiameter.uriRef))

        if self.hasHeight:
            for hasHeight in self.hasHeight:
                g.add((self.uriRef, ONTOIM["hasHeight"], hasHeight.uriRef))

        if self.hasTemporalEntity:
            g.add((self.uriRef, TI["hasTemporalEntity"],
                  self.hasTemporalEntity.uriRef))

        if self.hasHealthStatus:
            g.add(
                (self.uriRef, ONTOIM["hasHealthStatus"], self.hasHealthStatus.uriRef))
