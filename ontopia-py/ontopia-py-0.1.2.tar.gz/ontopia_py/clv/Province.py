from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .AdminUnitComponent import AdminUnitComponent

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class Province(AdminUnitComponent):
    __type__ = CLV["Province"]

    acronym: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.acronym:
            for acronym in self.acronym:
                g.add((self.uriRef, CLV["acronym"], acronym))
