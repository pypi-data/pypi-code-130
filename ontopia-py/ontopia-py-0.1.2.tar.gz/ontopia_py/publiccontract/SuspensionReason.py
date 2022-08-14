from __future__ import annotations

from ..ns import *
from .AmendmentRationale import AmendmentRationale


class SuspensionReason(AmendmentRationale):
    __type__ = PUBC["SuspensionReason"]
