# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tellmewhattodo',
 'tellmewhattodo.app',
 'tellmewhattodo.job',
 'tellmewhattodo.models']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'boto3>=1.24.43,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'requests>=2.28.1,<3.0.0',
 'streamlit>=1.11.1,<2.0.0']

entry_points = \
{'console_scripts': ['tellmewhattodo = tellmewhattodo.cli:cli']}

setup_kwargs = {
    'name': 'tellmewhattodo',
    'version': '2.1.1',
    'description': 'Simple app that checks for what to do and presents that in a website',
    'long_description': None,
    'author': 'Martin Morset',
    'author_email': 'mmo@one.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
