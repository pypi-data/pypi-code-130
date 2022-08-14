from rdflib import URIRef

from ..l0.Characteristic import Characteristic
from ..ns import *


class Status(Characteristic):
    __type__ = COV["Status"]


class Cancelled(Status):
    def __init__(self):
        self.uriRef = URIRef(COV["Cancelled"])


class Registered(Status):
    def __init__(self):
        self.uriRef = URIRef(COV["Registered"])


class UnderRegistration(Status):
    def __init__(self):
        self.uriRef = URIRef(COV["UnderRegistration"])
