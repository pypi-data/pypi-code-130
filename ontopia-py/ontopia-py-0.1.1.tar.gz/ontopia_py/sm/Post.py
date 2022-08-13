from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .UserAccount import UserAccount


class Post(Object):
    __type__ = SM["Post"]

    hasCreator: UserAccount = None
    postContent: Literal = None
    hasReply: List[Post] = None
    isReplyOf: List[Post] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasCreator:
            g.add((self.uriRef, SM["hasCreator"], self.hasCreator.uriRef))

        if self.postContent:
            g.add((self.uriRef, SM["postContent"], self.postContent))

        if self.hasReply:
            for hasReply in self.hasReply:
                g.add((self.uriRef, SM["hasReply"], hasReply.uriRef))

        if self.isReplyOf:
            for isReplyOf in self.isReplyOf:
                g.add((self.uriRef, SM["isReplyOf"], isReplyOf.uriRef))
