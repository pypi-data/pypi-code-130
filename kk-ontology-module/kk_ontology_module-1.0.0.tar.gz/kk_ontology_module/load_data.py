import pandas as pd
import pkg_resources

TEST_DATA = 'extras/m2dummyB_small.csv'

def load_data(filename=0, mapped_regimen='MAPPED_REGIMEN'):
    stream = pkg_resources.resource_stream(__name__, TEST_DATA)
    if filename:
        # If the user wants to upload their own ontology
        try:
            df = pd.read_csv(filename)
        except(FileNotFoundError):
            print("FileNotFoundError: Please double check the path and name of your data file.")
            return
    else:
        # Using the default ontology shipped with the package
        try:
            df = pd.read_csv(stream)
        except(FileNotFoundError):
            print("Error loading the test_data file shipped with this package.")
            return

    df = df.astype({mapped_regimen: str})
    return df
