# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['morningstreams', 'morningstreams.core']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0']

entry_points = \
{'console_scripts': ['morningstreams = morningstreams.cli:cli']}

setup_kwargs = {
    'name': 'morningstreams',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'S1M0N38',
    'author_email': 'bertolottosimone@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
