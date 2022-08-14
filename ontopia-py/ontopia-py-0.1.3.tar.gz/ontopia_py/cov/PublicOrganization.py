from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Organization import Organization

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .PublicOrgActivityType import PublicOrgActivityType
    from .PublicOrganizationCategory import PublicOrganizationCategory


class PublicOrganization(Organization):
    __type__ = COV["PublicOrganization"]

    hasPublicOrgActivityType: List[PublicOrgActivityType] = None
    hasCategory: PublicOrganizationCategory = None
    IPAcode: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasPublicOrgActivityType:
            for hasPublicOrgActivityType in self.hasPublicOrgActivityType:
                g.add(
                    (self.uriRef, COV["hasPublicOrgActivityType"], hasPublicOrgActivityType.uriRef))

        if self.hasCategory:
            g.add((self.uriRef, COV["hasCategory"], self.hasCategory.uriRef))

        if self.IPAcode:
            g.add((self.uriRef, COV["IPAcode"], self.IPAcode))
