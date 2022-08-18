from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.acco.Accommodation import Accommodation

from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .Booking import Booking
    from .Bookings import Bookings


class Accommodation(Accommodation):
    __type__ = ONTOIM["Accommodation"]

    hasBooking: List[Booking] = None
    hasBookings: List[Bookings] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasBooking:
            for hasBooking in self.hasBooking:
                g.add((self.uriRef, ONTOIM["hasBooking"], hasBooking.uriRef))

        if self.hasBookings:
            for hasBookings in self.hasBookings:
                g.add((self.uriRef, ONTOIM["hasBookings"], hasBookings.uriRef))
