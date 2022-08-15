# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exhaustion']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'exhaustion',
    'version': '1.0.0',
    'description': 'A tiny library to help in exhaustive testing of Boolean functions in Python.',
    'long_description': None,
    'author': 'Saul Johnson',
    'author_email': 'saul.a.johnson@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
