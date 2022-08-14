from __future__ import annotations

from typing import TYPE_CHECKING, List

from rdflib import URIRef

from ..l0.Topic import Topic
from ..ns import *

if TYPE_CHECKING:
    from rdflib import Graph

    from .Path import Path


class PathTheme(Topic):
    __type__ = PATHS["PathTheme"]

    isThemeOf: List[Path] = None

    def _addProperties(self, g: Graph):
        super()._addProperties(g)

        if self.isThemeOf:
            for isThemeOf in self.isThemeOf:
                g.add((self.uriRef, PATHS["isThemeOf"], isThemeOf.uriRef))


class Archaeological(PathTheme):
    def __init__(self):
        self.uriRef = URIRef(PATHS["Archaeological"])


class Cultural(PathTheme):
    def __init__(self):
        self.uriRef = URIRef(PATHS["Cultural"])


class Historical(PathTheme):
    def __init__(self):
        self.uriRef = URIRef(PATHS["Historical"])


class Naturalistic(PathTheme):
    def __init__(self):
        self.uriRef = URIRef(PATHS["Naturalistic"])


class Religious(PathTheme):
    def __init__(self):
        self.uriRef = URIRef(PATHS["Religious"])
