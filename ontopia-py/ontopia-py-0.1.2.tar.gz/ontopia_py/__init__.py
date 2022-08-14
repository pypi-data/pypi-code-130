from rdflib import RDF, Graph
from rdflib.namespace import (DC, DCAT, DCTERMS, FOAF, OWL, PROV, RDF, RDFS,
                              SKOS, XMLNS, XSD)

from .ConceptScheme import ConceptScheme
from .ns import *
from .Thing import Thing

VERSION = (0, 1, 2)

__author__ = 'Luca Martinelli'
__email__ = 'martinelliluca98@gmail.com'
__version__ = '.'.join(map(str, VERSION))
__description__ = 'A python package to create OntoPiA RDFs.'


def createGraph():
    # Create the graph
    g = Graph()

    g.bind("xsd", XSD)
    g.bind("foaf", FOAF)
    g.bind("owl", OWL)
    g.bind("dc", DC)
    g.bind("xml", XMLNS)
    g.bind("dct", DCTERMS)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("dcat", DCAT)
    g.bind("prov", PROV)
    g.bind("skos", SKOS)

    # Bind for OntoPiA
    g.bind("l0", L0)
    g.bind("trapit", TRANSP)
    g.bind("tiapit", TI)
    g.bind("smapit", SM)
    g.bind("rtapit", ROUTE)
    g.bind("roapit", RO)
    g.bind("pcapit", PUBC)
    g.bind("prjapit", PROJ)
    g.bind("potapit", POT)
    g.bind("poiapit", POI)
    g.bind("parkapit", PARK)
    g.bind("muapit", MU)
    g.bind("langapit", LANG)
    g.bind("iotapit", IOT)
    g.bind("indicator", INDIC)
    g.bind("herapit", HER)
    g.bind("chapit", CULTHER)
    g.bind("cpvapit", CPV)
    g.bind("cpsvapit", CPSV)
    g.bind("cpevapit", CPEV)
    g.bind("covapit", COV)
    g.bind("clvapit", CLV)
    g.bind("aopapit", PATHS)
    g.bind("acapit", ACOND)
    g.bind("accoapit", ACCO)
    g.bind("admsapit", ADMS)
    g.bind("cis", CIS)

    # Controlled vocabularies
    g.bind("eventtype", EVENTS_TYPE)
    g.bind("license", LICENSES)
    g.bind("geodist", GEO_DISTRIBUTION)
    g.bind("region", REGIONS)
    g.bind("province", PROVINCES)
    g.bind("country", COUNTRIES)
    g.bind("city", CITIES)
    g.bind("poiclass", POI_CLASSIFICATION)
    g.bind("accostar", ACCO_STAR_RATINGS)
    g.bind("accotype", ACCO_TYPES)
    g.bind("educationlevel", PERSON_EDULEVEL)
    g.bind("persontitle", PERSON_TITLE)
    g.bind("parentalrelation", PERSON_PARENTAL_REL)
    g.bind("legalstatus", ORG_LEGAL_STATUS)
    g.bind("ateco", ORG_ATECO)
    g.bind("s13", ORG_S13)
    g.bind("discipline", CUL_SUBJ)
    g.bind("culturalplace", CUL_PLACES)
    g.bind("routetype", ROUTE_TYPES)
    g.bind("authtype", AUTH_TYPES)
    g.bind("channel", EROGATION_CHANNELS)
    g.bind("interactionlevel", INTERACT_LEVEL)
    g.bind("ioservice", IO_SERVICE)
    g.bind("lifeevent", LIFE_EVENTS)
    g.bind("businessevent", BUSINESS_EVENTS)
    g.bind("datatheme", DATA_THEMES)
    g.bind("servicesector", SERVICE_SECTOR)
    g.bind("frequency", FREQUENCIES)

    return g

# Serialize RDF and save it in different extensions


def saveGraph(g, fileName):
    formats = [
        {"ext": "ttl", "fmt": "turtle"},
        {"ext": "rdf", "fmt": "xml"}
    ]

    for format in formats:
        ext = format["ext"]
        fmt = format["fmt"]

        with open("{}.{}".format(fileName, ext), "w", encoding="utf-8") as fp:
            fp.write(g.serialize(format=fmt))
