from typing import List

from rdflib import RDF, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, RDF, SKOS

from .ConceptScheme import ConceptScheme


class Thing:
    _dataset: URIRef = None
    _titles: List[Literal] = []
    uriRef: URIRef = None

    def __init__(self, id: str, baseUri: Namespace, dataset: ConceptScheme = None, titles: List[Literal] = []):
        self._dataset = dataset
        self._titles = titles

        self.uriRef = URIRef(baseUri[id])

    def _addProperties(self, g: Graph):
        pass

    def addToGraph(self, g: Graph, isTopConcept=False):
        g.add((self.uriRef, RDF.type, self.__type__))

        for title in self._titles:
            g.add((self.uriRef, DC.title, title))

        if self._dataset:
            g.add((self.uriRef, SKOS.inScheme, self._dataset.uriRef))

        if isTopConcept:
            g.add(
                (self._dataset.uriRef, SKOS.hasTopConcept, self.uriRef))

        self._addProperties(g)
