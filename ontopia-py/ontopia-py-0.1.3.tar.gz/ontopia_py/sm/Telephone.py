from __future__ import annotations

from typing import TYPE_CHECKING

from rdflib import Graph, Literal

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .OnlineContactPoint import OnlineContactPoint
    from .TelephoneType import TelephoneType


class Telephone(Object):
    __type__ = SM["Telephone"]

    hasTelephoneType: TelephoneType = None
    isTelephoneOf: OnlineContactPoint = None
    telephoneNumber: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasTelephoneType:
            g.add((self.uriRef, SM["hasTelephoneType"],
                  self.hasTelephoneType.uriRef))

        if self.isTelephoneOf:
            g.add((self.uriRef, SM["isTelephoneOf"],
                  self.isTelephoneOf.uriRef))

        if self.telephoneNumber:
            g.add((self.uriRef, SM["telephoneNumber"], self.telephoneNumber))
