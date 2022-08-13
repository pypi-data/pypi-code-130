# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jw_plyflatten']

package_data = \
{'': ['*']}

install_requires = \
['affine>=2.3.1,<3.0.0',
 'numpy>=1.23.1,<2.0.0',
 'plyfile>=0.7.4,<0.8.0',
 'pyproj>=3.3.1,<4.0.0',
 'rasterio>=1.3.0,<2.0.0']

setup_kwargs = {
    'name': 'jw-plyflatten',
    'version': '0.1.0',
    'description': 'Take a series of ply files and produce a digital elevation map',
    'long_description': None,
    'author': 'JaeWangL',
    'author_email': 'jnso5072@outlook.kr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
