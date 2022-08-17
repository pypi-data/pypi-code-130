# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bigbuy']

package_data = \
{'': ['*']}

install_requires = \
['api-session>=1.3.1,<2.0.0', 'requests>=2.25.1,<3.0.0']

setup_kwargs = {
    'name': 'pybigbuy',
    'version': '3.15.3',
    'description': 'BigBuy API client in Python',
    'long_description': '# PyBigBuy\n\n**PyBigBuy** is a Python wrapper around BigBuy’s API.',
    'author': 'Bixoto',
    'author_email': 'info@bixoto.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
