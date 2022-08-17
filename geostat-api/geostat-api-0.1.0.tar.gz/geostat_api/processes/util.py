from typing import Tuple

import requests
import pyproj
from pygeoapi.process.base import ProcessorExecuteError


SRC_CRS = pyproj.CRS.from_epsg(4326)


def load_ogc_features(uri: str) -> dict:
    """
    Load the OGC API features endpoint. If the endpoint is
    served by Geostat API, the properties are searched for an
    x, y, and v value.
    """
    # check if a full URI is given
    if not uri.startswith('http'):
        uri = f'http://localhost:5000/collections/{uri}/items?f=json&limit=10000'

    # request the data
    try:
        response = requests.get(uri)
        data = response.json()
    except Exception as e:
        raise ProcessorExecuteError(f'Could not load data from {uri}\nError Message: {str(e)}')

    # TODO: validate GeoJSON ?
    return data


def geojson_to_data(geojson: dict, value_name: str = 'value', target_crs: int = 3857) -> Tuple[list, list, list]:
    """"""
    # check if x and y are given directly
    if 'x' in geojson['features'][0]['properties'] and 'y' in geojson['features'][0]['properties']:
        x = [float(f['properties']['x']) for f in geojson['features']]
        y = [float(f['properties']['y']) for f in geojson['features']]
    else:
        TGT_CRS = pyproj.CRS.from_epsg(target_crs)
        TRANSFORMER = pyproj.Transformer.from_crs(SRC_CRS, TGT_CRS, always_xy=True)
        wgs_x = [float(f['geometry']['coordinates'][0]) for f in geojson['features']]
        wgs_y = [float(f['geometry']['coordinates'][1]) for f in geojson['features']]
        x, y = TRANSFORMER.transform(wgs_x, wgs_y)
    
    v = [float(f['properties'][value_name]) for f in geojson['features']]
    
    return x, y, v
