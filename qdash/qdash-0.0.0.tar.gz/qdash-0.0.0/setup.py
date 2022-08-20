# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qdash']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'qdash',
    'version': '0.0.0',
    'description': '',
    'long_description': None,
    'author': 'Qdash Contributors',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
