from __future__ import annotations

from ..mu.Value import Value
from ..ns import *
from .Cost import Cost


class FixedCost(Cost, Value):
    __type__ = CPSV["FixedCost"]
