# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nchainz', 'nchainz.tests']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nchainz',
    'version': '0.1.0',
    'description': 'Like 2 Chainz but better!',
    'long_description': None,
    'author': 'Lars Quentin',
    'author_email': 'lars@lquenti.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
