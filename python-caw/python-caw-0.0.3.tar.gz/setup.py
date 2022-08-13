# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycaw',
 'pycaw.defillama',
 'pycaw.etherscan',
 'pycaw.messari',
 'pycaw.messari.examples']

package_data = \
{'': ['*'], 'pycaw.messari': ['mappings/*']}

install_requires = \
['eth-utils==1.9.5',
 'pandas>=1.4.3,<2.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'requests>=2.28.1,<3.0.0',
 'web3>=5.30.0,<6.0.0']

setup_kwargs = {
    'name': 'python-caw',
    'version': '0.0.3',
    'description': 'A Python package for wrapping common Crypto APIs like Etherscan, Messari, CoinGecko, and Coin Market Cap',
    'long_description': None,
    'author': 'Unique-Divine',
    'author_email': 'realuniquedivine@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
