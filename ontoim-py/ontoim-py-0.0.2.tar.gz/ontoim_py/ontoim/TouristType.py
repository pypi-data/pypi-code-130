from __future__ import annotations

from ontopia_py.Thing import Thing
from rdflib import URIRef

from ..ns import *


class TouristType(Thing):
    __type__ = TI["TouristType"]


class Arrival(TouristType):
    def __init__(self):
        self.uriRef = URIRef(ONTOIM["Arrival"])


class Presence(TouristType):
    def __init__(self):
        self.uriRef = URIRef(ONTOIM["Presence"])
