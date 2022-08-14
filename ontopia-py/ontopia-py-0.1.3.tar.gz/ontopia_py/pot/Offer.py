from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Description import Description
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .PriceSpecification import PriceSpecification
    from .Ticket import Ticket
    from .UserType import UserType
    from .Validity import Validity


class Offer(Description):
    __type__ = POT["Currency"]

    hasPriceSpecification: List[PriceSpecification] = None
    hasValidity: List[Validity] = None
    includes: List[Ticket] = None
    description: List[Literal] = None
    hasEligibleUser: List[UserType] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasPriceSpecification:
            for hasPriceSpecification in self.hasPriceSpecification:
                g.add(
                    (self.uriRef, POT["hasPriceSpecification"], hasPriceSpecification.uriRef))

        if self.hasValidity:
            for hasValidity in self.hasValidity:
                g.add((self.uriRef, POT["hasValidity"], hasValidity.uriRef))

        if self.includes:
            for includes in self.includes:
                g.add((self.uriRef, POT["includes"], includes.uriRef))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.hasEligibleUser:
            for hasEligibleUser in self.hasEligibleUser:
                g.add(
                    (self.uriRef, POT["hasEligibleUser"], hasEligibleUser.uriRef))
