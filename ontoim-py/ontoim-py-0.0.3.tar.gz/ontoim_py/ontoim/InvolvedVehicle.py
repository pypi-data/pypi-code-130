from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .InvolvedEntity import InvolvedEntity

if TYPE_CHECKING:
    from rdflib import Graph

    from .InvolvedPerson import InvolvedPerson
    from .Vehicle import Vehicle


class InvolvedVehicle(InvolvedEntity):
    __type__ = ONTOIM["InvolvedVehicle"]

    hasBackPassenger: List[InvolvedPerson] = None
    hasFrontPassenger: List[InvolvedPerson] = None
    hasPassenger: List[InvolvedPerson] = None
    hasConducent: InvolvedPerson = None
    hasVehicle: Vehicle = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasConducent:
            g.add((self.uriRef, ONTOIM["hasConducent"],
                  self.hasConducent.uriRef))

        if self.hasVehicle:
            g.add((self.uriRef, ONTOIM["hasVehicle"], self.hasVehicle.uriRef))

        if self.hasBackPassenger:
            for hasBackPassenger in self.hasBackPassenger:
                g.add(
                    (self.uriRef, ONTOIM["hasBackPassenger"], hasBackPassenger.uriRef))

        if self.hasFrontPassenger:
            for hasFrontPassenger in self.hasFrontPassenger:
                g.add(
                    (self.uriRef, ONTOIM["hasFrontPassenger"], hasFrontPassenger.uriRef))

        if self.hasPassenger:
            for hasPassenger in self.hasPassenger:
                g.add(
                    (self.uriRef, ONTOIM["hasPassenger"], hasPassenger.uriRef))
