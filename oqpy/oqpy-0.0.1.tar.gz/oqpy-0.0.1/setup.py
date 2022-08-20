# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oqpy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'oqpy',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'OQpy Contributors',
    'author_email': 'oqpy.contributors@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
