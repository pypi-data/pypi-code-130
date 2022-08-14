from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from ..Thing import Thing

if TYPE_CHECKING:
    from rdflib import Graph

    from .Collection import Collection
    from .Description import Description
    from .Sequence import Sequence
    from .Topic import Topic


class Entity(Thing):
    __type__ = L0["Entity"]

    directlyFollows: List[Entity] = None
    directlyPrecedes: List[Entity] = None
    follows: List[Entity] = None
    hasDescription: List[Description] = None
    hasLastMember: List[Sequence] = None
    hasTopic: List[Topic] = None
    isFirstMemberOf: List[Sequence] = None
    isLastMemberOf: List[Sequence] = None
    isMemberOf: List[Collection] = None
    precedes: List[Entity] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.directlyFollows:
            for directlyFollows in self.directlyFollows:
                g.add(
                    (self.uriRef, L0["directlyFollows"], directlyFollows.uriRef))

        if self.directlyPrecedes:
            for directlyPrecedes in self.directlyPrecedes:
                g.add((self.uriRef, L0["directlyPrecedes"],
                       directlyPrecedes.uriRef))

        if self.follows:
            for follows in self.follows:
                g.add((self.uriRef, L0["follows"], follows.uriRef))

        if self.hasDescription:
            for hasDescription in self.hasDescription:
                g.add((self.uriRef, L0["hasDescription"],
                      hasDescription.uriRef))

        if self.hasLastMember:
            for hasLastMember in self.hasLastMember:
                g.add((self.uriRef, L0["hasLastMember"], hasLastMember.uriRef))

        if self.hasTopic:
            for hasTopic in self.hasTopic:
                g.add((self.uriRef, L0["hasTopic"], hasTopic.uriRef))

        if self.isFirstMemberOf:
            for isFirstMemberOf in self.isFirstMemberOf:
                g.add(
                    (self.uriRef, L0["isFirstMemberOf"], isFirstMemberOf.uriRef))

        if self.isLastMemberOf:
            for isLastMemberOf in self.isLastMemberOf:
                g.add((self.uriRef, L0["isLastMemberOf"],
                      isLastMemberOf.uriRef))

        if self.isMemberOf:
            for isMemberOf in self.isMemberOf:
                g.add((self.uriRef, L0["isMemberOf"], isMemberOf.uriRef))

        if self.precedes:
            for precedes in self.precedes:
                g.add((self.uriRef, L0["precedes"], precedes.uriRef))
