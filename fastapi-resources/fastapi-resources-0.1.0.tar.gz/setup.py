# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_resources',
 'fastapi_resources.resources',
 'fastapi_resources.routers']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.70.0,<0.71.0',
 'sqlmodel>=0.0.4,<0.0.5',
 'uvicorn[standard]>=0.15.0,<0.16.0']

setup_kwargs = {
    'name': 'fastapi-resources',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Ben Davis',
    'author_email': 'ben@bencdavis.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
