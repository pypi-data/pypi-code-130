## Defining the load function
from owlready2 import *
import pandas as pd

TEST_ONTO = "extras/CancerOntology.owl"

def load_onto(filename):
    return get_ontology(filename).load()

# print(load_onto(TEST_ONTO))