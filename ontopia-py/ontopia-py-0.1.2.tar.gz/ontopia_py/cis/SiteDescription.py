from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Description import Description
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from .Attribute import Attribute


class SiteDescription(Description):
    __type__ = CIS["SiteDescription"]

    hasAttribute: List[Attribute] = None
    description: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasAttribute:
            for hasAttribute in self.hasAttribute:
                g.add((self.uriRef, CIS["hasAttribute"], hasAttribute.uriRef))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))
