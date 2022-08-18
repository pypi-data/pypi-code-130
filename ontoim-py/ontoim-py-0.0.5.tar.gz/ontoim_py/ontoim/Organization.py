from __future__ import annotations

from typing import TYPE_CHECKING, List

from ontopia_py.cov.Organization import Organization

from ..ns import *

if TYPE_CHECKING:
    from ontopia_py.clv.Address import Address
    from rdflib import Graph, Literal

    from .Employees import Employees
    from .Heritage import Heritage


class Organization(Organization):
    __type__ = ONTOIM["Organization"]

    hasEmployees: List[Employees] = None
    hasHeritage: List[Heritage] = None
    hasLocalUnitAddress: List[Address] = None
    endActivityDate: Literal = None
    liquidationDate: Literal = None
    bankruptcyDate: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasEmployees:
            for hasEmployees in self.hasEmployees:
                g.add(
                    (self.uriRef, ONTOIM["hasEmployees"], hasEmployees.uriRef))

        if self.hasHeritage:
            for hasHeritage in self.hasHeritage:
                g.add((self.uriRef, ONTOIM["hasHeritage"], hasHeritage.uriRef))

        if self.hasLocalUnitAddress:
            for hasLocalUnitAddress in self.hasLocalUnitAddress:
                g.add(
                    (self.uriRef, ONTOIM["hasLocalUnitAddress"], hasLocalUnitAddress.uriRef))

        if self.endActivityDate:
            g.add(
                (self.uriRef, ONTOIM["endActivityDate"], self.endActivityDate))

        if self.liquidationDate:
            g.add(
                (self.uriRef, ONTOIM["liquidationDate"], self.liquidationDate))

        if self.bankruptcyDate:
            g.add(
                (self.uriRef, ONTOIM["bankruptcyDate"], self.bankruptcyDate))
