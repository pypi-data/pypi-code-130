# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['geohexgrid']

package_data = \
{'': ['*']}

install_requires = \
['Rtree>=1.0.0', 'geopandas>=0.11.1']

setup_kwargs = {
    'name': 'geohexgrid',
    'version': '1.0.0',
    'description': "A Python library for making geographic hexagon grids like QGIS's `create grid` function",
    'long_description': None,
    'author': 'Alex Raichev',
    'author_email': 'araichev@mrcagney.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/mrcagney/geohexgrid',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4',
}


setup(**setup_kwargs)
