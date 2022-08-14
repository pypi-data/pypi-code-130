from __future__ import annotations

from typing import TYPE_CHECKING

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class CivicNumbering(Characteristic):
    __type__ = CLV["CivicNumbering"]

    streetNumber: Literal = None
    exponent: Literal = None
    metric: Literal = None
    peculiarity: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.streetNumber:
            g.add((self.uriRef, CLV["streetNumber"], self.streetNumber))

        if self.exponent:
            g.add((self.uriRef, CLV["exponent"], self.exponent))

        if self.metric:
            g.add((self.uriRef, CLV["metric"], self.metric))

        if self.peculiarity:
            g.add((self.uriRef, CLV["peculiarity"], self.peculiarity))
