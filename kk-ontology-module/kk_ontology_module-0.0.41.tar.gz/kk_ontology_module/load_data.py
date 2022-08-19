import pandas as pd
import pkg_resources

TEST_DATA = 'extras/m2dummyB_small.csv'

def load_data(filename=0, mapped_regimen='MAPPED_REGIMEN'):
    stream = pkg_resources.resource_stream(__name__, TEST_DATA)
    if filename:
        # If the user wants to upload their own ontology
        df = pd.read_csv(filename) 
    else:
        # Using the default ontology shipped with the package
        df = pd.read_csv(stream)
    df = df.astype({mapped_regimen: str})
    return df
