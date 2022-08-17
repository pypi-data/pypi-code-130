from typing import Tuple

from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError
from skgstat import Variogram

from geostat_api.processes import util


PROCESS_METADATA = {
    'version': '0.1.0',
    'id': 'variogram',
    'title': {
        'en': 'Variogram',
        'de': 'Variogram'
    },
    'description': {
        'en': 'Calculate a Variogram for the input dataset.',
        'de': 'Bereichnung eines Variogramms für den angegebenen Datensatz.',
    },
    'keywords': ['variogram', 'geostatistics', 'SciKit-GStat'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'Information',
        'href': 'https://mmaelicke.github.io/scikit-gstat/reference/variogram.html',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'data': {
            'title': 'Input Dataset',
            'description': 'Valid Geojson or URI of the OGC API features endpoint to be used as input.',
            'schema': {
                'oneOf': [
                    {
                        'type': 'string'
                    },
                    {
                        'allOf': [
                            {
                                'format': 'geojson-feature-collection',
                            },
                            {
                                '$ref': 'https://geojson.org/schema/FeatureCollection.json'
                            }
                        ]
                    }
                ]
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['OGC API', 'points']
        },
        'nLags': {
            'title': 'Lag classes',
            'description': 'The number of lag classes to be created. If not given, defaults to 10.',
            'schema': {
                'type': 'number'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['lags', 'bins' 'n_lags']
        },
        'model': {
            'title': 'Theoretical variogram model',
            'description': "Theoretical variogram model used for fitting. If not given, defaults to 'spherical'",
            'schema': {
                'type': 'string'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['model', 'theoretical variogram']
        },
        'estimator': {
            'title': 'Semi-Variance Estimator',
            'description': "Semi-variance estimator used to calculate observation similiary. If not given, defaults to 'matheron'",
            'schema': {
                'type': 'string'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['estimator', 'semi-variance']
        },
        'distFunc': {
            'title': 'Distance function',
            'description': "Distance functions to evaluate proximity in space. If not given, defaults to 'euclidean'.",
            'schema': {
                'type': 'string'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['distance', 'Euklidean']
        },
        'binFunc': {
            'title': 'Binning function',
            'description': "Binning function to group lag classes. If not given, defaults to 'even'.",
            'schema': {
                'type': 'string'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['binning', 'lag classes']
        },
        'fitMethod': {
            'title': 'Automatic fitting function',
            'description': "Automatic fitting function for the theoretical function. If not given, defaults to 'trf'.",
            'schema': {
                'type': 'string'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['fitting', 'least squares']
        },
        'fitSigma': {
            'title': 'Fitting Weights',
            'description': "Fitting weight function for fitting procedure. If not given, defaults to 'None'.",
            'schema': {
                'type': 'string'
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['fitting', 'weights']
        },
        'maxlag': {
            'title': 'Maximum lag distance',
            'description': "Maximum lag distance to form point pairs. Can be 'median', 'mean' or a ratio of maximum distance (0 - 1).\
                If type is number and larger than 1, an absolute value is used. If not given, defaults to 'None'.",
            'schema': {
                'oneOf': [
                    {'type': 'number'},
                    {'type': 'string'}
                ]
            },
            'minOccurs': 0,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['lag', 'maxlag', 'maximum lag']
        },
    },
    'outputs': {
        'params': {
            'title': 'Variogram parameter',
            'description': 'JSON representation of the fitted variogram parameters',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        },
        'sample': {
            'title': 'Sample data',
            'description': 'JSON representation of the sample data used to calculate this variogram.',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'data_uri': 'http://localhost:5000',
            'n_lags': 15,
        }
    }
}


class VariogramProcessor(BaseProcessor):
    """"""
    def __init__(self, processor_def) -> None:
        """Initialize the VariogramProcessor"""
        super().__init__(processor_def, PROCESS_METADATA)

    def execute(self, data) -> Tuple[str, dict]:
        """"""
        # get the uri
        if 'data' not in data:
            raise ProcessorExecuteError('Missing data or data URI')
        
        # hanle uri
        if isinstance(data['data'], str):
            geojson = util.load_ogc_features(data['data'])
        elif isinstance(data['data'], dict):
            geojson = data['data']
        else:
            raise ProcessorExecuteError("Invalid data type for 'data' parameter. Has to be a OGC API features endpoint or valid geojson.")
        
        # load data
        try:
            x, y, v = util.geojson_to_data(geojson)
        except Exception as e:
            raise ProcessorExecuteError(f"Error loading data: {e}")

        # get the params
        vparams = {}
        vparams['n_lags'] = data.get('nLags', 10)
        vparams['model'] = data.get('model', 'spherical')
        vparams['estimator'] = data.get('estimator', 'matheron')
        vparams['dist_func'] = data.get('distFunc', 'euclidean')
        vparams['bin_func'] = data.get('binFunc', 'even')
        vparams['fit_method'] = data.get('fitMethod', 'trf')
        vparams['fit_sigma'] = data.get('fitSigma')
        vparams['maxlag'] = data.get('maxlag')
        

        # create a variogram
        try:
            vario = Variogram(list(zip(x, y)), v, **vparams)
            params = vario.describe(flat=True)
        except Exception as e:
            raise ProcessorExecuteError(f'Could not create variogram: {e}')

        # create the output
        outputs = {
            'params': {
                'id': 'params',
                'value': params
            },
            'sample':{
                'id': 'sample',
                'value': {'x': x, 'y': y, 'v': v}
            }
        }

        return 'application/json', outputs

