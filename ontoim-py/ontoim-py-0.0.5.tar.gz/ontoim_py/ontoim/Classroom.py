from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.l0.Location import Location

from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class Classroom(Location):
    __type__ = ONTOIM["Classroom"]

    name: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))
