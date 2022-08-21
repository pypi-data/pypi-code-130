import pandas as pd

example_irr = pd.read_csv('example_irr.csv', header=6, skipfooter=12, engine='python', index_col='time')
example_load = pd.read_csv('example_load.csv', sep=',')


