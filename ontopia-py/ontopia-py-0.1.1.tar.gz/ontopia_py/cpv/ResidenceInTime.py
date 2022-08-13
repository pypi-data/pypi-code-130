from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from ..ti.TimeIndexedEvent import TimeIndexedEvent

if TYPE_CHECKING:
    from rdflib import Graph

    from ..clv.Address import Address
    from .Person import Person


class ResidenceInTime(TimeIndexedEvent):
    __type__ = CPV["ResidenceInTime"]

    residenceInLocation: Address = None
    isResidenceInTimeOf: Person = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.residenceInLocation:
            g.add((self.uriRef, CPV["residenceInLocation"],
                  self.residenceInLocation.uriRef))

        if self.isResidenceInTimeOf:
            g.add((self.uriRef, CPV["isResidenceInTimeOf"],
                  self.isResidenceInTimeOf.uriRef))
