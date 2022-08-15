from __future__ import annotations

from ontopia_py.cis.CulturalEvent import CulturalEvent

from ..ns import *
from .PublicEvent import PublicEvent


class CulturalEvent(CulturalEvent, PublicEvent):
    __type__ = ONTOIM["CulturalEvent"]
