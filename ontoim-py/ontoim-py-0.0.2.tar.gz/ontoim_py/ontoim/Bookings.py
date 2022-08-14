from __future__ import annotations

from .DemographicObservation import DemographicObservation
from ..ns import *


class Bookings(DemographicObservation):
    __type__ = ONTOIM["Bookings"]
