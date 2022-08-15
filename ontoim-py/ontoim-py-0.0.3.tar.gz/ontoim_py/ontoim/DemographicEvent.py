from __future__ import annotations

from typing import TYPE_CHECKING

from ontopia_py.l0.EventOrSituation import EventOrSituation

from ..ns import *

if TYPE_CHECKING:
    from ontopia_py.clv.Feature import Feature
    from ontopia_py.cpv.Person import Person
    from rdflib import Graph, Literal


class DemographicEvent(EventOrSituation):
    __type__ = ONTOIM["DemographicEvent"]

    hasDemographicReference: Person = None
    hasSpatialCoverage: Feature = None
    date: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasDemographicReference:
            g.add((self.uriRef, ONTOIM["hasDemographicReference"],
                  self.hasDemographicReference.uriRef))

        if self.hasSpatialCoverage:
            g.add(
                (self.uriRef, CLV["hasSpatialCoverage"], self.hasSpatialCoverage.uriRef))

        if self.date:
            g.add((self.uriRef, ONTOIM["date"], self.date))
