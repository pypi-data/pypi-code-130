from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .UserAccount import UserAccount


class SocialMedia(Object):
    __type__ = SM["SocialMedia"]

    socialMediaName: Literal = None
    issuesAccount: List[UserAccount] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.socialMediaName:
            g.add((self.uriRef, SM["socialMediaName"], self.socialMediaName))

        if self.issuesAccount:
            for issuesAccount in self.issuesAccount:
                g.add((self.uriRef, SM["issuesAccount"], issuesAccount.uriRef))
