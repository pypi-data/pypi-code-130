from __future__ import annotations

from ..ns import *
from .Hospital import Hospital


class PrivateHospital(Hospital):
    __type__ = ONTOIM["PrivateHospital"]
