from __future__ import annotations

from typing import TYPE_CHECKING

from rdflib import Graph, Literal

from ..l0.Object import Object
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .EmailType import EmailType
    from .OnlineContactPoint import OnlineContactPoint


class Email(Object):
    __type__ = SM["Email"]

    hasEmailType: EmailType = None
    isEmailOf: OnlineContactPoint = None
    emailAddress: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasEmailType:
            g.add((self.uriRef, SM["hasEmailType"], self.hasEmailType.uriRef))

        if self.isEmailOf:
            g.add((self.uriRef, SM["isEmailOf"], self.isEmailOf.uriRef))

        if self.emailAddress:
            g.add((self.uriRef, SM["emailAddress"], self.emailAddress))
