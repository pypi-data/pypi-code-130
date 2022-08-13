from __future__ import annotations

from typing import TYPE_CHECKING, List

from rdflib import Graph

from ..l0.EventOrSituation import EventOrSituation
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from ..ti.TimeInterval import TimeInterval
    from .Address import Address


class AddressInTime(EventOrSituation):
    __type__ = CLV["AddressInTime"]

    atTime: List[TimeInterval] = None
    nextAddress: List[AddressInTime] = None
    prevAddress: List[AddressInTime] = None
    withAddress: Address = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.atTime:
            for atTime in self.atTime:
                g.add(
                    (self.uriRef, CLV["atTime"], atTime.uriRef))

        if self.nextAddress:
            for nextAddress in self.nextAddress:
                g.add(
                    (self.uriRef, CLV["nextAddress"], nextAddress.uriRef))

        if self.prevAddress:
            for prevAddress in self.prevAddress:
                g.add(
                    (self.uriRef, CLV["prevAddress"], prevAddress.uriRef))

        if self.isAddressInTimeFor:
            for isAddressInTimeFor in self.isAddressInTimeFor:
                g.add(
                    (self.uriRef, CLV["isAddressInTimeFor"], isAddressInTimeFor.uriRef))

        if self.withAddress:
            g.add((self.uriRef, CLV["withAddress"], self.withAddress.uriRef))
