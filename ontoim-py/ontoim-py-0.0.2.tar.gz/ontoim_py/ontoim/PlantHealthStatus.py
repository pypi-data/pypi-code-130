from __future__ import annotations

from ontopia_py.Thing import Thing
from rdflib import URIRef

from ..ns import *


class PlantHealthStatus(Thing):
    __type__ = TI["PlantHealthStatus"]


class Bad(PlantHealthStatus):
    def __init__(self):
        self.uriRef = URIRef(ONTOIM["Bad"])


class Dead(PlantHealthStatus):
    def __init__(self):
        self.uriRef = URIRef(ONTOIM["Dead"])


class Fair(PlantHealthStatus):
    def __init__(self):
        self.uriRef = URIRef(ONTOIM["Fair"])


class Good(PlantHealthStatus):
    def __init__(self):
        self.uriRef = URIRef(ONTOIM["Good"])


class Stump(PlantHealthStatus):
    def __init__(self):
        self.uriRef = URIRef(ONTOIM["Stump"])
