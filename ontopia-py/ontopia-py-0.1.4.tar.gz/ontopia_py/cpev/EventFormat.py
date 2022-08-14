from rdflib import URIRef

from ..l0.Characteristic import Characteristic
from ..ns import *


class EventFormat(Characteristic):
    __type__ = CPEV["EventFormat"]


class Physical(EventFormat):
    def __init__(self):
        self.uriRef = URIRef(CPEV["Physical"])


class Virtual(EventFormat):
    def __init__(self):
        self.uriRef = URIRef(CPEV["Virtual"])
