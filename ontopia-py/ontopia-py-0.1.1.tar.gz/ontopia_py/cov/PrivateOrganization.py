from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..ns import *
from .Organization import Organization

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .PrivateOrgActivityType import PrivateOrgActivityType


class PrivateOrganization(Organization):
    __type__ = COV["PrivateOrganization"]

    hasPrivateOrgActivityType: List[PrivateOrgActivityType] = None
    REANumber: Literal = None
    businessObjective: List[Literal] = None
    VATnumber: Literal = None
    startingActivityDate: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasPrivateOrgActivityType:
            for hasPrivateOrgActivityType in self.hasPrivateOrgActivityType:
                g.add(
                    (self.uriRef, COV["hasPrivateOrgActivityType"], hasPrivateOrgActivityType.uriRef))

        if self.REANumber:
            g.add((self.uriRef, COV["REANumber"], self.REANumber))

        if self.businessObjective:
            for businessObjective in self.businessObjective:
                g.add(
                    (self.uriRef, COV["businessObjective"], businessObjective))

        if self.VATnumber:
            g.add((self.uriRef, COV["VATnumber"], self.VATnumber))

        if self.startingActivityDate:
            g.add(
                (self.uriRef, COV["startingActivityDate"], self.startingActivityDate))
