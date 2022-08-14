from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from ..route.Route import Route

if TYPE_CHECKING:
    from rdflib import Graph

    from ..l0.Agent import Agent


class Pathway(Route):
    __type__ = PATHS["Pathway"]

    hasMaintainer: List[Agent] = None
    hasSurveillance: List[Agent] = None
    hasMember: List[Agent] = None
    hasFirstMember: List[Agent] = None
    hasLastMember: List[Agent] = None
    hasQuantityOfPaving: List[Agent] = None
    hasSecurityLevel: List[Agent] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasMaintainer:
            for hasMaintainer in self.hasMaintainer:
                g.add(
                    (self.uriRef, PATHS["hasMaintainer"], hasMaintainer.uriRef))

        if self.hasSurveillance:
            for hasSurveillance in self.hasSurveillance:
                g.add(
                    (self.uriRef, PATHS["hasSurveillance"], hasSurveillance.uriRef))

        if self.hasMember:
            for hasMember in self.hasMember:
                g.add((self.uriRef, PATHS["hasMember"], hasMember.uriRef))

        if self.hasFirstMember:
            for hasFirstMember in self.hasFirstMember:
                g.add(
                    (self.uriRef, PATHS["hasFirstMember"], hasFirstMember.uriRef))

        if self.hasLastMember:
            for hasLastMember in self.hasLastMember:
                g.add(
                    (self.uriRef, PATHS["hasLastMember"], hasLastMember.uriRef))

        if self.hasQuantityOfPaving:
            for hasQuantityOfPaving in self.hasQuantityOfPaving:
                g.add(
                    (self.uriRef, PATHS["hasQuantityOfPaving"], hasQuantityOfPaving.uriRef))

        if self.hasSecurityLevel:
            for hasSecurityLevel in self.hasSecurityLevel:
                g.add(
                    (self.uriRef, PATHS["hasSecurityLevel"], hasSecurityLevel.uriRef))
