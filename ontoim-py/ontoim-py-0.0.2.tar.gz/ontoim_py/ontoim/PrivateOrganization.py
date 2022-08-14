from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.cov.PrivateOrganization import PrivateOrganization

from ..ns import *
from .Organization import Organization

if TYPE_CHECKING:
    from rdflib import Graph

    from .CompanyDemographicCategory import CompanyDemographicCategory
    from .OrganizationSection import OrganizationSection


class PrivateOrganization(Organization, PrivateOrganization):
    __type__ = ONTOIM["PrivateOrganization"]

    hasDemographicCategory: List[CompanyDemographicCategory] = None
    hasOrganizationSection: List[OrganizationSection] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasDemographicCategory:
            for hasDemographicCategory in self.hasDemographicCategory:
                g.add(
                    (self.uriRef, ONTOIM["hasDemographicCategory"], hasDemographicCategory.uriRef))

        if self.hasOrganizationSection:
            for hasOrganizationSection in self.hasOrganizationSection:
                g.add(
                    (self.uriRef, ONTOIM["hasOrganizationSection"], hasOrganizationSection.uriRef))
