from rdflib import URIRef

from ..l0.Characteristic import Characteristic
from ..ns import *


class ParticipationType(Characteristic):
    __type__ = COV["ParticipationType"]


class Direct(ParticipationType):
    def __init__(self):
        self.uriRef = URIRef(COV["Direct"])


class Indirect(ParticipationType):
    def __init__(self):
        self.uriRef = URIRef(COV["Indirect"])
