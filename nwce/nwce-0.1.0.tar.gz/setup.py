# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nwce']

package_data = \
{'': ['*']}

install_requires = \
['pre-commit>=2.17.0,<3.0.0']

setup_kwargs = {
    'name': 'nwce',
    'version': '0.1.0',
    'description': 'Network Configuration Editor',
    'long_description': None,
    'author': 'DESNOË Olivier (Canal Plus)',
    'author_email': 'olivier.desnoe@canal-plus.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
