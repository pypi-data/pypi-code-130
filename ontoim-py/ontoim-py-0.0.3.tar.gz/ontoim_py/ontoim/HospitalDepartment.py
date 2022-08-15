from __future__ import annotations

from ..ns import *
from .Hospital import Hospital


class HospitalDepartment(Hospital):
    __type__ = ONTOIM["HospitalDepartment"]
