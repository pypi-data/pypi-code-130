from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .Channel import Channel

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class EmailChannel(Channel):
    __type__ = CPSV["EmailChannel"]

    emailAddress: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.emailAddress:
            g.add((self.uriRef, SM["emailAddress"], self.emailAddress))