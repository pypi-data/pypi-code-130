from __future__ import annotations

from typing import TYPE_CHECKING, List, Union

from ..l0.EventOrSituation import EventOrSituation
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..mu.Value import Value
    from ..ti.TimeInterval import TimeInterval


class Validity(EventOrSituation):
    __type__ = POT["Validity"]

    hasDuration: List[Union[Value, TimeInterval]] = None
    description: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasDuration:
            for hasDuration in self.hasDuration:
                g.add((self.uriRef, TI["hasDuration"], hasDuration.uriRef))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))
