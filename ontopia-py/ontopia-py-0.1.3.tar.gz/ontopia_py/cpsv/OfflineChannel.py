from __future__ import annotations

from ..ns import *
from .Channel import Channel


class OfflineChannel(Channel):
    __type__ = CPSV["OfflineChannel"]
