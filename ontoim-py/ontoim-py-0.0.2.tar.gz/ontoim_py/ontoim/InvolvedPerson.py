from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .InvolvedEntity import InvolvedEntity

if TYPE_CHECKING:
    from ontopia_py.cpv.Person import Person
    from rdflib import Graph

    from .InvolvedPersonStatus import InvolvedPersonStatus


class InvolvedPerson(InvolvedEntity):
    __type__ = ONTOIM["InvolvedPerson"]

    hasPerson: InvolvedPersonStatus = None
    hasPerson: Person = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasInvolvedPersonStatus:
            g.add((self.uriRef, ONTOIM["hasInvolvedPersonStatus"],
                  self.hasInvolvedPersonStatus.uriRef))

        if self.hasPerson:
            g.add((self.uriRef, ONTOIM["hasPerson"], self.hasPerson.uriRef))
