from typing import List, Dict
import re
import os
import hashlib

from yaml import load, Loader, dump, Dumper
from skgstat_uncertainty.models import DataUpload
from skgstat_uncertainty.api import API
from shapely.geometry import Point
from shapely.geometry.collection import GeometryCollection

from geostat_api import CONFIG_FILE, DATA_PATH, DB_NAME, OPENAPI_FILE


def skgstat_to_shapely(dataset: DataUpload) -> GeometryCollection:
    """Convert the WGS84 coordinates of a DataUpload instance to a shapely GeometryCollection"""
    # get the coordinates
    x, y = dataset.to_wgs84()

    # create the collection
    col = GeometryCollection([Point(*xy) for xy in zip(x, y)])

    return col


def create_resource_config(dataset: DataUpload, title: str = None, links: List[dict] = []) -> dict:
    """Create a PyGeoAPI resources config for the given dataset"""
    # scrape for DOIs in origin
    if 'origin' in dataset.data:
        dois = re.findall(r'(10[.]\d{4,}/[a-z 0-9 -]+)', dataset.data['origin'])
    else:
        dois = []
    if 'doi' in dataset.data:
        dois.append(dataset.data['doi'])
    for doi in dois:
        links.append({'type': 'text/html', 'rel': 'cite-as', 'title': f'DOI: {doi}', 'href': f'https://doi.org/{doi}'})
        

    if 'crs' in dataset.data:
        # TODO: derive using DataUpload Model
        spatial_extent = {'bbox': [list(skgstat_to_shapely(dataset).bounds)], 'crs': 'http://www.opengis.net/def/OGC/1.3/CRS84'}
    else:
        spatial_extent = {'bbox': [[-180, -90, 180, 90]], 'crs': 'http://www.opengis.net/def/OGC/1.3/CRS84'}
    
    # create the basic layout
    conf = {
        'type': 'collection',
        'title': title if title is not None else dataset.upload_name,
        'description': dataset.data['description'] if 'description' in dataset.data else 'This dataset has no description',
        'keywords': ['geostatistics', 'hydrocode', *[k for k in dataset.data.get('keywords', [])]],
        'links': [
            {
                'type': 'text/html',
                'rel': 'external',
                'title': 'Hydrocode Geostatistics educational applications',
                'href': 'https://geostat.hydrocode.de'
            },

        ],
        'extents': {
            'spatial': spatial_extent
        },
        'providers': [{
            'type': 'feature',
            'name': 'geostat_api.feature_provider.DataUploadProvider',
            'id_field': 'id',
            'data': dataset.id
        }]
    }
    
    return conf


def create_process_config() -> Dict[str, dict]:
    """"""
    processes = {}

    # Variogram
    processes['variogram'] = {
        'type': 'process',
        'processor': {'name': 'geostat_api.processes.variogram.VariogramProcessor'},
    }

    # hello-world
    processes['hello-world'] = {
        'type': 'process',
        'processor': {'name': 'HelloWorld'},
    }

    return processes


def get_db_hash():
    # hash the database
    with open(os.path.join(DATA_PATH, DB_NAME), 'br') as f:
        return hashlib.sha256(f.read()).hexdigest()


def reosurces_are_updated():
    """Check if the reosurces need to be updated"""
    # load the hash from the current config file
    with open(CONFIG_FILE, 'r') as f:
        current_hash = f.readline().replace('# ', '').replace('\n', '')
    
    # get the db hash
    db_hash = get_db_hash()
    
    return current_hash == db_hash


def update_resources(drop_old: bool = True):
    """Update the resources section of the config file"""
    # load the config
    with open(CONFIG_FILE, 'r') as f:
        api_conf = load(f, Loader=Loader)

    # create an api instance
    api = API(data_path=DATA_PATH, db_name=DB_NAME)

    # get all sample datasets
    names = api.get_upload_names(data_type='sample')

    # resources container
    resources = {} if drop_old else api_conf.get('resources', {})

    # add each of the names
    for data_id in names.keys():
        # get the dataset
        dataset = api.get_upload_data(id=data_id)

        # create the resource config
        resource_config = create_resource_config(dataset)

        # derive the identifier
        # slug = dataset.upload_name.replace(' ', '_').lower()

        resources[f'{dataset.id}'] = resource_config

    # get processes
    processes = create_process_config()
    resources.update(processes)

    # update the config
    api_conf['resources'] = resources

    # write the config
    with open(CONFIG_FILE, 'w') as f:
        f.write(dump(api_conf, Dumper=Dumper, default_flow_style=False))

    # write the current hash
    db_hash = get_db_hash()
    with open(CONFIG_FILE, 'r') as f:
        f_content = f.read()
    with open(CONFIG_FILE, 'w') as f:
        f.write(f'# {db_hash}\n{f_content}')


def deploy_resources(force: bool = False):
    """Deploy the resources"""
    if not force:
        do_run = not reosurces_are_updated()
    else:
        do_run = True
    # if the sah is the same, do nothing
    if not do_run:
        print('Database is up to date, no need to update', flush=True)
        return
    
    # update the resources
    print('Updating OGC API resources...', end='', flush=True)
    update_resources()
    print('done', flush=True)

    # deploy
    print('Generating OpenAPI specifications...', end='', flush=True)
    os.system(f'pygeoapi openapi generate {CONFIG_FILE} > {OPENAPI_FILE}')
    print('done', flush=True)


if __name__ == '__main__':
    import fire
    fire.Fire(deploy_resources)
