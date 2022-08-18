from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.l0.Object import Object

from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class VideoCommunicationService(Object):
    __type__ = ONTOIM["VideoCommunicationService"]

    name: List[Literal] = None
    serviceURL: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))

        if self.serviceURL:
            for serviceURL in self.serviceURL:
                g.add((self.uriRef, ONTOIM["serviceURL"], serviceURL))
