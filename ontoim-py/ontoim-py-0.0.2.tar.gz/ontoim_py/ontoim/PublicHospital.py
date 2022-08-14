from __future__ import annotations

from ..ns import *
from .Hospital import Hospital


class PublicHospital(Hospital):
    __type__ = ONTOIM["PublicHospital"]
