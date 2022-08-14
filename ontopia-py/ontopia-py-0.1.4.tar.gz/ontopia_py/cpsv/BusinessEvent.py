from __future__ import annotations

from ..ns import *
from .EventOrSituation import EventOrSituation


class BusinessEvent(EventOrSituation):
    __type__ = CPSV["BusinessEvent"]
