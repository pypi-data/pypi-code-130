# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chchart_parser']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'chchart-parser',
    'version': '1.0.0',
    'description': 'Parser for clone hero .chart files',
    'long_description': None,
    'author': 'Dogeek',
    'author_email': 'simon.bordeyne@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
