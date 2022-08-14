from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .Channel import Channel

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class WebSiteChannel(Channel):
    __type__ = CPSV["WebSiteChannel"]

    URL: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.URL:
            g.add((self.uriRef, SM["URL"], self.URL))
