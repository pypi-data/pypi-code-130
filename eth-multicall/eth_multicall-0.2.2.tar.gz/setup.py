# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eth_multicall']

package_data = \
{'': ['*']}

install_requires = \
['web3>=5.30.0,<6.0.0']

setup_kwargs = {
    'name': 'eth-multicall',
    'version': '0.2.2',
    'description': 'Uses Multicall v3 and eth_abi encode + decoder api to fetch multiple json-rpc queries all at once',
    'long_description': '# MultiCall\n\ncall web3 multiple times instead of one time\n\nhelps with querying list of data from multiple contracts \n\n# MultiChain \n\nSupports Multicall at proposed chains listed below :\n\n',
    'author': 'Nfel',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/NFEL/eth_muticall',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
