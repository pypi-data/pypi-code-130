from __future__ import annotations

from typing import TYPE_CHECKING

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .OnlineContactPoint import OnlineContactPoint


class WebSite(Object):
    __type__ = SM["WebSite"]

    isWebSiteOf: OnlineContactPoint = None
    URL: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isWebSiteOf:
            g.add((self.uriRef, SM["isWebSiteOf"], self.isWebSiteOf.uriRef))

        if self.URL:
            g.add((self.uriRef, SM["URL"], self.URL))
