from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.System import System
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .FormalFramework import FormalFramework
    from .Requirement import Requirement
    from .Service import Service


class Rule(System):
    __type__ = CPSV["Rule"]

    implementsFF: List[FormalFramework] = None
    isFollowedByService: List[Service] = None
    specifiesReq: List[Requirement] = None
    description: List[Literal] = None
    name: List[Literal] = None
    referenceDoc: List[Literal] = None
    identifier: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.implementsFF:
            for implementsFF in self.implementsFF:
                g.add((self.uriRef, CPSV["implementsFF"], implementsFF.uriRef))

        if self.isFollowedByService:
            for isFollowedByService in self.isFollowedByService:
                g.add(
                    (self.uriRef, CPSV["isFollowedByService"], isFollowedByService.uriRef))

        if self.specifiesReq:
            for specifiesReq in self.specifiesReq:
                g.add((self.uriRef, CPSV["specifiesReq"], specifiesReq.uriRef))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))

        if self.referenceDoc:
            for referenceDoc in self.referenceDoc:
                g.add((self.uriRef, CPSV["referenceDoc"], referenceDoc))

        if self.identifier:
            g.add((self.uriRef, L0["identifier"], self.identifier))
