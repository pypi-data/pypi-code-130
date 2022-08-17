import os

__version__ = '0.1.0'

# some path settings
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

if 'PYGEOAPI_DATA_PATH' not in os.environ:
    os.environ['PYGEOAPI_DATA_PATH'] = '/home/mirko/Dropbox/python/skgstat_uncertainty/data'
if 'PYGEOAPI_DB_NAME' not in os.environ:
    os.environ['PYGEOAPI_DB_NAME'] = 'data.db'
if 'PYGEOAPI_CONFIG' not in os.environ:
    os.environ['PYGEOAPI_CONFIG'] = os.path.join(BASE_PATH, 'config/pygeoapi-config.yml')
if 'PYGEOAPI_OPENAPI' not in os.environ:
    os.environ['PYGEOAPI_OPENAPI'] = os.path.join(BASE_PATH, 'config/openapi-config.yml')
if 'PYGEOAPI_BASE_URL' not in os.environ:
    os.environ['PYGEOAPI_BASE_URL'] = 'http://localhost:5000/'

DATA_PATH = os.environ['PYGEOAPI_DATA_PATH']
DB_NAME = os.environ['PYGEOAPI_DB_NAME']
CONFIG_FILE = os.environ['PYGEOAPI_CONFIG']
OPENAPI_FILE = os.environ['PYGEOAPI_OPENAPI']