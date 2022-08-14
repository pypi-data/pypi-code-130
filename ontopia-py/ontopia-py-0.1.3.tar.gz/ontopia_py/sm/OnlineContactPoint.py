from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .ContactPoint import ContactPoint

if TYPE_CHECKING:
    from rdflib import Graph

    from ..Thing import Thing
    from .Email import Email
    from .Telephone import Telephone
    from .UserAccount import UserAccount
    from .WebSite import WebSite


class OnlineContactPoint(ContactPoint):
    __type__ = SM["OnlineContactPoint"]

    hasEmail: List[Email] = None
    hasCertifiedEmail: List[Email] = None
    hasTelephone: List[Telephone] = None
    hasUserAccount: List[UserAccount] = None
    hasWebSite: List[WebSite] = None
    isOnlineContactPointOf: List[Thing] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasEmail:
            for hasEmail in self.hasEmail:
                g.add((self.uriRef, SM["hasEmail"], hasEmail.uriRef))

        if self.hasCertifiedEmail:
            for hasCertifiedEmail in self.hasCertifiedEmail:
                g.add(
                    (self.uriRef, SM["hasCertifiedEmail"], hasCertifiedEmail.uriRef))

        if self.hasTelephone:
            for hasTelephone in self.hasTelephone:
                g.add((self.uriRef, SM["hasTelephone"], hasTelephone.uriRef))

        if self.hasUserAccount:
            for hasUserAccount in self.hasUserAccount:
                g.add((self.uriRef, SM["hasUserAccount"],
                      hasUserAccount.uriRef))

        if self.hasWebSite:
            for hasWebSite in self.hasWebSite:
                g.add((self.uriRef, SM["hasWebSite"], hasWebSite.uriRef))

        if self.isOnlineContactPointOf:
            for isOnlineContactPointOf in self.isOnlineContactPointOf:
                g.add(
                    (self.uriRef, SM["isOnlineContactPointOf"], isOnlineContactPointOf.uriRef))
