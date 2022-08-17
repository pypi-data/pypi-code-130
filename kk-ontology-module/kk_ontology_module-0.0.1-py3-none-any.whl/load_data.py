import pandas as pd

TEST_DATA = 'extras/m2dummyB_small.csv'

def load_data(filename, mapped_regimen='MAPPED_REGIMEN'):
    df = pd.read_csv(filename)
    # df = df.astype({'MAPPED_REGIMEN': str})
    df = df.astype({mapped_regimen: str})
    return df

# print(load_data(TEST_DATA)['MAPPED_REGIMEN'])