from rdflib import URIRef

from ..ns import *
from ..l0.Characteristic import Characteristic


class GeometryType(Characteristic):
    __type__ = CLV["GeometryType"]


class Box(GeometryType):
    def __init__(self):
        self.uriRef = URIRef(CLV["Box"])


class Line(GeometryType):
    def __init__(self):
        self.uriRef = URIRef(CLV["Line"])


class Point(GeometryType):
    def __init__(self):
        self.uriRef = URIRef(CLV["Point"])


class Polygon(GeometryType):
    def __init__(self):
        self.uriRef = URIRef(CLV["Polygon"])
