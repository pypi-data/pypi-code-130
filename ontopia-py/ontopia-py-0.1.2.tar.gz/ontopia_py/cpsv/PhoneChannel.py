from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .Channel import Channel

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class PhoneChannel(Channel):
    __type__ = CPSV["PhoneChannel"]

    telephoneNumber: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.telephoneNumber:
            g.add((self.uriRef, SM["telephoneNumber"], self.telephoneNumber))
