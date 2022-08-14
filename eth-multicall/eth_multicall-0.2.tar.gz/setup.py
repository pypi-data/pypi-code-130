# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['eth_multicall']
install_requires = \
['web3>=5.30.0,<6.0.0']

setup_kwargs = {
    'name': 'eth-multicall',
    'version': '0.2',
    'description': 'Uses Multicall v3 and eth_abi encode + decoder api to fetch multiple json-rpc queries all at once',
    'long_description': None,
    'author': 'Nfel',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
