from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..l0.Description import Description
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal

    from ..cov.Organization import Organization
    from ..sm.WebSite import WebSite
    from .PathPlan import PathPlan
    from .PathTheme import PathTheme
    from .Pathway import Pathway
    from .QuantifiedPathwayPaving import QuantifiedPathwayPaving


class Path(Description):
    __type__ = PATHS["Path"]

    hasGovernanceOrgan: List[Organization] = None
    hasRoute: List[Pathway] = None
    hasTripPlan: List[PathPlan] = None
    hasWebSite: List[WebSite] = None
    encountersPath: List[Path] = None
    hasAltRoute: List[Pathway] = None
    hasDeviation: List[Pathway] = None
    hasQuantifiedPathwayPaving: List[QuantifiedPathwayPaving] = None
    hasTheme: List[PathTheme] = None
    hasPrefRoute: Pathway = None
    description: List[Literal] = None
    name: List[Literal] = None
    pathNumber: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.hasGovernanceOrgan:
            for hasGovernanceOrgan in self.hasGovernanceOrgan:
                g.add(
                    (self.uriRef, PATHS["hasGovernanceOrgan"], hasGovernanceOrgan.uriRef))

        if self.hasRoute:
            for hasRoute in self.hasRoute:
                g.add((self.uriRef, ROUTE["hasRoute"], hasRoute.uriRef))

        if self.hasTripPlan:
            for hasTripPlan in self.hasTripPlan:
                g.add((self.uriRef, ROUTE["hasTripPlan"], hasTripPlan.uriRef))

        if self.hasWebSite:
            for hasWebSite in self.hasWebSite:
                g.add((self.uriRef, SM["hasWebSite"], hasWebSite.uriRef))

        if self.encountersPath:
            for encountersPath in self.encountersPath:
                g.add(
                    (self.uriRef, PATHS["encountersPath"], encountersPath.uriRef))

        if self.hasAltRoute:
            for hasAltRoute in self.hasAltRoute:
                g.add((self.uriRef, ROUTE["hasAltRoute"], hasAltRoute.uriRef))

        if self.hasDeviation:
            for hasDeviation in self.hasDeviation:
                g.add(
                    (self.uriRef, ROUTE["hasDeviation"], hasDeviation.uriRef))

        if self.hasQuantifiedPathwayPaving:
            for hasQuantifiedPathwayPaving in self.hasQuantifiedPathwayPaving:
                g.add(
                    (self.uriRef, PATHS["hasQuantifiedPathwayPaving"], hasQuantifiedPathwayPaving.uriRef))

        if self.hasTheme:
            for hasTheme in self.hasTheme:
                g.add((self.uriRef, PATHS["hasTheme"], hasTheme.uriRef))

        if self.hasPrefRoute:
            g.add((self.uriRef, ROUTE["hasPrefRoute"],
                  self.hasPrefRoute.uriRef))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))

        if self.pathNumber:
            for pathNumber in self.pathNumber:
                g.add((self.uriRef, PATHS["pathNumber"], pathNumber))
