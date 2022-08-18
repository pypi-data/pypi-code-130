from __future__ import annotations

from .DemographicEvent import DemographicEvent
from ..ns import *


class Subscriber(DemographicEvent):
    __type__ = ONTOIM["Subscriber"]
