from .ns import *
from ontopia_py import createGraph as cg, saveGraph

VERSION = (0, 0, 5)

__author__ = 'Luca Martinelli'
__email__ = 'martinelliluca98@gmail.com'
__version__ = '.'.join(map(str, VERSION))
__description__ = 'A python package to create OntoIM RDFs.'


def createGraph():
    # Create the graph
    g = cg()

    # Ontology
    g.bind("ontoim", ONTOIM)

    # Controlled vocabularies
    g.bind("accidentcircumstances", ACCIDENT_CIRCUMSTANCES)
    g.bind("accidenttypes", ACCIDENT_TYPES)
    g.bind("associationcategories", ASSOCIATION_CATEGORIES)
    g.bind("civilstatuscategories", CIVIL_STATUS_CATEGORIES)
    g.bind("companydemographiccategories", COMPANY_DEMOGRAPHIC_CATEGORIES)
    g.bind("heritagetypes", HERITAGE_TYPES)
    g.bind("involvedpersonstatuses", INVOLVED_PERSON_STATUSES)
    g.bind("landregistrycategories", LAND_REGISTRY_CATEGORIES)
    g.bind("organizationsections", ORGANIZATION_SECTIONS)
    g.bind("pavementtypes", PAVEMENT_TYPES)
    g.bind("revelationunits", REVELATION_UNITS)
    g.bind("roadcategories", ROAD_CATEGORIES)
    g.bind("roadcontexts", ROAD_CONTEXTS)
    g.bind("roadsignalpresencetypes", ROAD_SIGNAL_PRESENCE_TYPES)
    g.bind("roadsignaltypes", ROAD_SIGNAL_TYPES)
    g.bind("roadtypes", ROAD_TYPES)
    g.bind("roadbedtypes", ROADBED_TYPES)
    g.bind("schooltypes", SCHOOL_TYPES)
    g.bind("vehiclecategories", VEHICLE_CATEGORIES)
    g.bind("wastecategories", WASTE_CATEGORIES)
    g.bind("weatherconditions", WEATHER_CONDITIONS)

    return g
