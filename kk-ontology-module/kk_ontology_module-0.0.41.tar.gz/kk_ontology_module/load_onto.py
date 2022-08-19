## Defining the load function
from owlready2 import *
import pkg_resources
import pandas as pd

TEST_ONTO = "extras/CancerOntology.owl"

def load_onto(filename=0):
    stream = pkg_resources.resource_filename(__name__, TEST_ONTO)
    if filename:
        o = get_ontology(filename).load()
    else:
        o = get_ontology(stream).load()
    # resources.open_resource(TEST_ONTO)
    return o

# print(load_onto(TEST_ONTO))