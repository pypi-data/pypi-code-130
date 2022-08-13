from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .OnlineContactPoint import OnlineContactPoint
    from .Post import Post
    from .SocialMedia import SocialMedia


class UserAccount(Object):
    __type__ = SM["UserAccount"]

    isAccountIssuedBy: SocialMedia = None
    isUserAccountOf: OnlineContactPoint = None
    URL: Literal = None
    userAccountName: Literal = None
    isCreatorOf: List[Post] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isAccountIssuedBy:
            g.add((self.uriRef, SM["isAccountIssuedBy"],
                  self.isAccountIssuedBy.uriRef))

        if self.isUserAccountOf:
            g.add((self.uriRef, SM["isUserAccountOf"],
                  self.isUserAccountOf.uriRef))

        if self.URL:
            g.add((self.uriRef, SM["URL"], self.URL))

        if self.userAccountName:
            g.add((self.uriRef, SM["userAccountName"], self.userAccountName))

        if self.isCreatorOf:
            for isCreatorOf in self.isCreatorOf:
                g.add((self.uriRef, SM["isCreatorOf"], isCreatorOf.uriRef))
