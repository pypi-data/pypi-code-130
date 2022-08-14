from __future__ import annotations

from ..l0.EventOrSituation import EventOrSituation
from ..ns import *


class Payment(EventOrSituation):
    __type__ = PUBC["Payment"]