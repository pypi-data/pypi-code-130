from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.EventOrSituation import EventOrSituation
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Organization import Organization


class ChangeEvent(EventOrSituation):
    __type__ = COV["ChangeEvent"]

    orginalOrganization: List[Organization] = None
    resultingOrganization: List[Organization] = None
    description: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.orginalOrganization:
            for orginalOrganization in self.orginalOrganization:
                g.add(
                    (self.uriRef, COV["orginalOrganization"], orginalOrganization.uriRef))

        if self.resultingOrganization:
            for resultingOrganization in self.resultingOrganization:
                g.add(
                    (self.uriRef, COV["resultingOrganization"], resultingOrganization.uriRef))

        if self.description:
            for description in self.description:
                g.add(
                    (self.uriRef, L0["description"], description))
