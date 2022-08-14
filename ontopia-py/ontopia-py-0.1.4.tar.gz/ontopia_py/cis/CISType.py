from __future__ import annotations

from typing import TYPE_CHECKING, List

from rdflib import URIRef

from ..l0.Characteristic import Characteristic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph, Literal


class CISType(Characteristic):
    __type__ = CIS["CISType"]

    description: List[Literal] = None
    name: List[Literal] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.description:
            for description in self.description:
                g.add((self.uriRef, L0["description"], description))

        if self.name:
            for name in self.name:
                g.add((self.uriRef, L0["name"], name))


class ArchaeologicalArea(CISType):
    def __init__(self):
        self.uriRef = URIRef(CIS["ArchaeologicalArea"])


class ArchaeologicalPark(CISType):
    def __init__(self):
        self.uriRef = URIRef(CIS["ArchaeologicalPark"])


class Cinema(CISType):
    def __init__(self):
        self.uriRef = URIRef(CIS["Cinema"])


class CulturalLandscapeAsset(CISType):
    def __init__(self):
        self.uriRef = URIRef(CIS["CulturalLandscapeAsset"])


class CultResearchCenter(CISType):
    def __init__(self):
        self.uriRef = URIRef(CIS["CultResearchCenter"])


class HolderOfArchive(CISType):
    def __init__(self):
        self.uriRef = URIRef(CIS["HolderOfArchive"])


class Library(CISType):
    def __init__(self):
        self.uriRef = URIRef(CIS["Library"])


class MonumentalArea(CISType):
    def __init__(self):
        self.uriRef = URIRef(CIS["MonumentalArea"])


class Museum(CISType):
    def __init__(self):
        self.uriRef = URIRef(CIS["Museum"])


class Theatre(CISType):
    def __init__(self):
        self.uriRef = URIRef(CIS["Theatre"])
