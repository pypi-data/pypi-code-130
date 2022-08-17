import requests
from skgstat_uncertainty.models import DataUpload
import pyproj

FEATRURE_URL = '{protocol}://{host}:{port}/collections/{col_name}/items?f=json&limit={limit}'
PROCESS_URL = '{protocol}://{host}:{port}/processes/{process_name}/{action}?f=json'

SRC_CRS = pyproj.CRS.from_epsg(4326)
TGT_CRS = pyproj.CRS.from_epsg(3857)
TRANSFORMER = pyproj.Transformer.from_crs(SRC_CRS, TGT_CRS, always_xy=True)


def get_remote_data(collection_name: str = None, url: str = FEATRURE_URL, limit: int = 1500, return_type: str = 'skgstat', **kwargs) -> DataUpload:
    """get the data from the remote server"""
    # get the options
    protocol = kwargs.get('protocol', 'http')
    host = kwargs.get('host', 'localhost')
    port = kwargs.get('port', '5000')

    # build the URI
    uri = url.format(col_name=collection_name, limit=limit, host=host, port=port, protocol=protocol)
    
    # request the data
    r = requests.get(uri)
    data = r.json()

    # extract the data
    if 'x' in data['features'][0]['properties'] and 'y' in data['features'][0]['properties']:
        x = [float(f['properties']['x']) for f in data['features']]
        y = [float(f['properties']['y']) for f in data['features']]
    else:
        wgs_x = [float(f['geometry']['coordinates'][0]) for f in data['features']]
        wgs_y = [float(f['geometry']['coordinates'][1]) for f in data['features']]
        x, y = TRANSFORMER.transform(wgs_x, wgs_y)
        
        # TODO reproject here
    v = [float(f['properties']['value']) for f in data['features']]

    # if return type is raw, return only the most necessary data
    if return_type == 'raw':
        return x, y, v

    # build the metadata
    try:
        meta = {'upload_name': data['metadata']['upload_name'], 'data_type': data['metadata']['data_type']}
    except KeyError:
        if return_type == 'skgstat':
            raise AttributeError("The GeoJSON did not contain a 'metadata' key, which at least needs to include a 'upload_name' and 'data_type' key")
        else:
            meta = {}
    
    # put in the other stuff
    meta['data'] = dict(x=x, y=y, v=v, **{k: v for k,v in data['metadata'].items() if k not in ['upload_name', 'data_type']})
    
    # return
    if return_type == 'json':
        return meta
    else:
        return DataUpload(**meta)


def execute(process_name: str, inputs: dict = {}, url: str = PROCESS_URL, **kwargs) -> dict:
    """"""
    # get the options
    protocol = kwargs.get('protocol', 'http')
    host = kwargs.get('host', 'localhost')
    port = kwargs.get('port', '5000')

    # build the URI
    uri = url.format(process_name=process_name, host=host, port=port, protocol=protocol, action='execution')
    
    # request the data
    r = requests.post(uri, json={'inputs': inputs})
    return r
    data = r.json()

    return data