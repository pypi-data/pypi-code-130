from __future__ import annotations

from typing import TYPE_CHECKING

from ontopia_py.l0.Entity import Entity

from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .AccidentCircumstance import AccidentCircumstance


class InvolvedEntity(Entity):
    __type__ = ONTOIM["InvolvedEntity"]

    hasAccidentCircumstance: AccidentCircumstance = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasAccidentCircumstance:
            g.add((self.uriRef, ONTOIM["hasAccidentCircumstance"],
                  self.hasAccidentCircumstance.uriRef))
