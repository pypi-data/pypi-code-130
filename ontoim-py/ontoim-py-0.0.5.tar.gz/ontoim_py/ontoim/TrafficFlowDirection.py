from __future__ import annotations

from ontopia_py.Thing import Thing
from rdflib import URIRef

from ..ns import *


class TrafficFlowDirection(Thing):
    __type__ = TI["TrafficFlowDirection"]


class In(TrafficFlowDirection):
    def __init__(self):
        self.uriRef = URIRef(ONTOIM["In"])


class Out(TrafficFlowDirection):
    def __init__(self):
        self.uriRef = URIRef(ONTOIM["Out"])
