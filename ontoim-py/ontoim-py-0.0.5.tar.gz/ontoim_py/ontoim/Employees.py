from __future__ import annotations

from .DemographicObservation import DemographicObservation
from ..ns import *


class Employees(DemographicObservation):
    __type__ = ONTOIM["Employees"]
