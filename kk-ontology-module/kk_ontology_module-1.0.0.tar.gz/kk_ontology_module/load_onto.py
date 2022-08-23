## Defining the load function
from owlready2 import *
import pkg_resources

TEST_ONTO = "extras/CancerOntology.owl"

def load_onto(filename=0):
    stream = pkg_resources.resource_filename(__name__, TEST_ONTO)
    if filename:
        try:
            o = get_ontology(filename).load()
        except(FileNotFoundError):
            print("FileNotFoundError: Please double check the path and name of your ontology file.")
            return
    else:
        try:
            o = get_ontology(stream).load()
        except(FileNotFoundError):
            print("Error loading the ontology file shipped with this package.")
            return
    
    return o