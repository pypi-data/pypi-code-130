from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Address import Address


class InternalAccess(Characteristic):
    __type__ = CLV["InternalAccess"]

    refersToExternalAccess: List[Address] = None
    staircase: List[Literal] = None
    flatNumber: Literal = None
    building: Literal = None
    exponent: Literal = None
    floor: Literal = None
    yard: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.refersToExternalAccess:
            for refersToExternalAccess in self.refersToExternalAccess:
                g.add(
                    (self.uriRef, CLV["refersToExternalAccess"], refersToExternalAccess.uriRef))

        if self.staircase:
            for staircase in self.staircase:
                g.add((self.uriRef, CLV["staircase"], staircase))

        if self.flatNumber:
            g.add((self.uriRef, CLV["flatNumber"], self.flatNumber))

        if self.building:
            g.add((self.uriRef, CLV["building"], self.building))

        if self.exponent:
            g.add((self.uriRef, CLV["exponent"], self.exponent))

        if self.floor:
            g.add((self.uriRef, CLV["floor"], self.floor))

        if self.yard:
            g.add((self.uriRef, CLV["yard"], self.yard))
