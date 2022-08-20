# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['monquery']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'monquery',
    'version': '0.3.0',
    'description': 'A library for HTTP query string to MongoDB queries translation',
    'long_description': None,
    'author': 'monomonedula',
    'author_email': 'valh@tuta.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monomonedula/monquery',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
