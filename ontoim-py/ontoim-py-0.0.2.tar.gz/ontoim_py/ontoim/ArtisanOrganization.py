from __future__ import annotations

from typing import TYPE_CHECKING

from ..ns import *
from .PrivateOrganization import PrivateOrganization

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class ArtisanOrganization(PrivateOrganization):
    __type__ = ONTOIM["ArtisanOrganization"]

    artisanRegisterCode: Literal = None
    artisanRegistrationDate: Literal = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.artisanRegisterCode:
            g.add(
                (self.uriRef, ONTOIM["artisanRegisterCode"], self.artisanRegisterCode))

        if self.artisanRegistrationDate:
            g.add(
                (self.uriRef, ONTOIM["artisanRegistrationDate"], self.artisanRegistrationDate))
