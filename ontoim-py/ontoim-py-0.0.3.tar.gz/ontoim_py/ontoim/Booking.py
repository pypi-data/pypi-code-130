from __future__ import annotations

from .DemographicEvent import DemographicEvent
from ..ns import *


class Booking(DemographicEvent):
    __type__ = ONTOIM["Booking"]
