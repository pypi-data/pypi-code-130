# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ngrammer_keras']

package_data = \
{'': ['*']}

install_requires = \
['einops', 'keras>=2.9.0,<3.0.0', 'sympy>=1.10.1,<2.0.0']

setup_kwargs = {
    'name': 'ngrammer-keras',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Pieter Blomme',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
