import pandas as pd
import pkg_resources

stream = pkg_resources.resource_stream(__name__, 'example_irr.csv')

print('get path: ',stream)


# example_irr = pd.read_csv(stream, header=6, skipfooter=12, engine='python', index_col='time')

# example_irr = pd.read_csv('example_irr.csv', header=6, skipfooter=12, engine='python', index_col='time')
# example_load = pd.read_csv('example_load.csv', sep=',')


