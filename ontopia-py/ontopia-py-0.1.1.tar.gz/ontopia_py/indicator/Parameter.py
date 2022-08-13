from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from ..mu.Value import Value


class Parameter(Characteristic):
    __type__ = INDIC["Parameter"]

    parametrizes: List[Value] = None
    subParameter: List[Parameter] = None
    superParameter: List[Parameter] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.parametrizes:
            for parametrizes in self.parametrizes:
                g.add(
                    (self.uriRef, INDIC["parametrizes"], parametrizes.uriRef))

        if self.subParameter:
            for subParameter in self.subParameter:
                g.add(
                    (self.uriRef, INDIC["subParameter"], subParameter.uriRef))

        if self.superParameter:
            for superParameter in self.superParameter:
                g.add(
                    (self.uriRef, INDIC["superParameter"], superParameter.uriRef))
