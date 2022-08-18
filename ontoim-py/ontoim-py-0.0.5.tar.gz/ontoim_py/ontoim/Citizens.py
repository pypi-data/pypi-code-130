from __future__ import annotations

from .DemographicObservation import DemographicObservation
from ..ns import *


class Citizens(DemographicObservation):
    __type__ = ONTOIM["Citizens"]
