from typing import List
import os
import pyproj
from pygeoapi.provider.base import BaseProvider

from skgstat_uncertainty.api import API
from skgstat_uncertainty.models import DataUpload

from geostat_api import DATA_PATH, DB_NAME


def extract_features(dataset: DataUpload):
    features = []
    
    # get the data from the database
    data = dataset.data

    # extract coordinates
    if 'crs' in data:
        X, Y = dataset.to_wgs84()
        proj = pyproj.CRS.from_epsg(data['crs'])
    else:
        X = data['x']
        Y = data['y']
        proj = None

    for i, (coord_x, coord_y, v, x, y) in enumerate(zip(X, Y, data['v'], data['x'], data['y'])):    
        f = {
            'type': 'Feature',
            'id': i,
            'geometry': {
                'type': 'Point',
                'coordinates': [coord_x, coord_y]
            },
            'properties': {
                'value': v,
                'x': x,
                'y': y
                
            }
        }

        # add original  crs info
        if proj is not None:
            f['properties']['crs'] = f"EPSG:{data['crs']}  {proj.name}"
        features.append(f)

    return features


def filt(f: dict, properties: List[str]):
    """Filter a single Feature by its properties"""
    prop = {k:v for k, v in f['properties'].items() if k in properties}
    return {**{k:v for k, v in f.items() if k != 'properties'}, 'properties': prop}


def reorder_and_filter_features(features: List[dict], properties: List[str], sortby: List[str]) -> List[dict]:
    """Apply a property filter and sort the features, without assigning new IDs"""
    features = [filt(f, properties) for f in features]

    # sorting
    if len(sortby) > 0:
        sortfunc = lambda k: tuple([k['properties']['sorter'].strip('+-') for sorter in sortby])
        features = features.sort(key=sortfunc, reverse=features[0]['properties'][sortby[0]].startwith('-'))
    
    # return
    return features

class DataUploadProvider(BaseProvider):
    """connect to our database and load data"""
    def __init__(self, provider_def):
        BaseProvider.__init__(self, provider_def)

        # create the api
        self.api = API(data_path=DATA_PATH, db_name=DB_NAME)

        # load the dataset
        self.dataset = self.api.get_upload_data(id=self.data)
        self.features = extract_features(self.dataset)
        self.fields = self.get_fields()

    def get_fields(self):
        return {
            'value': {'type': 'number'},
            'x': {'type': 'number'},
            'y': {'type': 'number'},
            'crs': {'type': 'string'}
        }

    def query(self, startindex=0, limit=100, skipGeometry: bool = False, properties: List[str] = [], sortby: List[str] = [], **kwargs):
        # get the features
        features = self.features

        # limit the response
        if startindex < len(features):
            features = features[startindex:startindex+limit]
        else:
            return {'code': 400, 'description': 'startindex out of range'}
        
        # properties to be included
        if len(properties) == 0:
            properties.extend(list(self.features[0]['properties'].keys()))

        # get the sortby argument
        if isinstance(sortby, str):
            sortby = [sortby]
        if sortby is None:
            sortby = []

        # filter and sort the features
        features = reorder_and_filter_features(features, properties, sortby)

        # geometry
        if skipGeometry:
            features = [{**{k:v for k, v in f.items() if k != 'geometry'}, 'geometry': None} for f in features]

        # build metadata
        meta = dict(
            upload_name=self.dataset.upload_name,
            data_type=self.dataset.data_type,
            **{k: v for k, v in self.dataset.data.items() if k not in ['x', 'y', 'v', 'field']}
        )

        # build the geoJSON respone
        geojson = {
            'type': 'FeatureCollection',
            'features': features,
            'metadata': meta
        }

        return geojson

    def get(self, identifier=None, **kwargs):
        return [f for f in self.features if f['id'] == int(identifier)].pop()
