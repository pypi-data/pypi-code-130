from __future__ import annotations

from typing import TYPE_CHECKING, List, Union

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..l0.EventOrSituation import EventOrSituation
    from ..l0.Location import Location
    from .Validity import Validity


class Ticket(Object):
    __type__ = POT["Ticket"]

    hasValidity: List[Validity] = None
    description: List[Literal] = None
    forAccessTo: List[Union[EventOrSituation, Location]] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasValidity:
            for hasValidity in self.hasValidity:
                g.add((self.uriRef, POT["hasValidity"], hasValidity.uriRef))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.forAccessTo:
            for forAccessTo in self.forAccessTo:
                g.add((self.uriRef, POT["forAccessTo"], forAccessTo.uriRef))