import pandas as pd

df = pd.read_csv('pv_sizing/example_data/example_irr.csv', header=6, skipfooter=12, engine='python', index_col='time')