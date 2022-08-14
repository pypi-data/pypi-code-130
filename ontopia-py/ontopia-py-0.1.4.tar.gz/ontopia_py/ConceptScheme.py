from typing import List

from rdflib import RDF, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, RDF, RDFS, SKOS


class ConceptScheme:
    label: List[Literal] = []
    creator: List[Literal] = []
    description: List[Literal] = []
    comment: List[Literal] = []

    def __init__(self, uri: Namespace = None):
        self.uriRef = URIRef(uri)

    def addToGraph(self, g: Graph):
        g.add((self.uriRef, RDF.type, SKOS.ConceptScheme))

        self._addProperties(g)

    def _addProperties(self, g: Graph):
        if self.label:
            for label in self.label:
                g.add((self.uriRef, RDFS.label, label))

        if self.creator:
            for creator in self.creator:
                g.add((self.uriRef, DC.creator, creator))

        if self.description:
            for description in self.description:
                g.add((self.uriRef, DC.description, description))

        if self.comment:
            for comment in self.comment:
                g.add((self.uriRef, RDFS.comment, comment))
