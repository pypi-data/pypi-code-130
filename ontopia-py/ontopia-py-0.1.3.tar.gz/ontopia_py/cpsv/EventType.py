from __future__ import annotations

from rdflib import URIRef

from ..l0.Characteristic import Characteristic
from ..ns import *


class EventType(Characteristic):
    __type__ = CPSV["EventType"]


class Closing(EventType):
    def __init__(self):
        self.uriRef = URIRef(CPSV["Closing"])


class Doing(EventType):
    def __init__(self):
        self.uriRef = URIRef(CPSV["Doing"])


class Starting(EventType):
    def __init__(self):
        self.uriRef = URIRef(CPSV["Starting"])


class StartingCrossBorder(EventType):
    def __init__(self):
        self.uriRef = URIRef(CPSV["StartingCrossBorder"])
