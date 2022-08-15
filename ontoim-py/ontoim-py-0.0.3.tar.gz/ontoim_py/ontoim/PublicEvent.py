from __future__ import annotations

from ontopia_py.cpev.PublicEvent import PublicEvent

from ..ns import *
from .Event import Event


class PublicEvent(Event, PublicEvent):
    __type__ = ONTOIM["PublicEvent"]
