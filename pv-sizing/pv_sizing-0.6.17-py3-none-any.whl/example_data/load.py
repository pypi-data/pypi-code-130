import pandas as pd
import os
this_dir, this_filename = os.path.split(__file__)
DATA_PATH = os.path.join(this_dir, "example_irr.csv")

data = pd.read_csv(DATA_PATH, header=6, skipfooter=12, engine='python', index_col='time')
