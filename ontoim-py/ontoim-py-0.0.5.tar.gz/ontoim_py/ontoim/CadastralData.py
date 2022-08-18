from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.l0.Object import Object

from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .CadastralCategory import CadastralCategory


class CadastralData(Object):
    __type__ = ONTOIM["CadastralData"]

    hasCadastralCategory: List[CadastralCategory] = None
    map: Literal = None
    sheet: Literal = None
    subordinate: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasCadastralCategory:
            g.add(
                (self.uriRef, ONTOIM["hasCadastralCategory"], self.hasCadastralCategory.uriRef))

        if self.hasMembers:
            for hasMembers in self.hasMembers:
                g.add(
                    (self.uriRef, ONTOIM["hasMembers"], hasMembers.uriRef))

        if self.hasReferent:
            for hasReferent in self.hasReferent:
                g.add(
                    (self.uriRef, ONTOIM["hasReferent"], hasReferent.uriRef))

        if self.hasSubscription:
            for hasSubscription in self.hasSubscription:
                g.add(
                    (self.uriRef, ONTOIM["hasSubscription"], hasSubscription.uriRef))

        if self.map:
            g.add((self.uriRef, ONTOIM["map"], self.map))

        if self.sheet:
            g.add((self.uriRef, ONTOIM["sheet"], self.sheet))

        if self.subordinate:
            g.add((self.uriRef, ONTOIM["subordinate"], self.subordinate))
