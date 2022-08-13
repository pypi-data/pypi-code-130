# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['babbagecoin',
 'babbagecoin.client',
 'babbagecoin.common',
 'babbagecoin.master',
 'babbagecoin.miner']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.3,<3.0.0',
 'cryptography>=36.0.1,<37.0.0',
 'marshmallow>=3.14.1,<4.0.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'requests>=2.27.1,<3.0.0',
 'sentry-sdk[flask]>=1.5.8,<2.0.0']

setup_kwargs = {
    'name': 'babbagecoin',
    'version': '0.1.0',
    'description': 'Second edition of project Babbage, create a blockchain from scratch (in a weekend)',
    'long_description': None,
    'author': 'Quentin Garchery',
    'author_email': 'garchery.quentin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
