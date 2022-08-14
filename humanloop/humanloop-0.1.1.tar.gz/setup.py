# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['humanloop',
 'humanloop.api',
 'humanloop.api.models',
 'humanloop.cli',
 'humanloop.sdk',
 'humanloop.shared']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'pytest>=7.1.2,<8.0.0',
 'rich>=12.4.4,<13.0.0',
 'uplink>=0.9.7,<0.10.0']

entry_points = \
{'console_scripts': ['humanloop = humanloop.cli:humanloop']}

setup_kwargs = {
    'name': 'humanloop',
    'version': '0.1.1',
    'description': 'CLI and Python bindings for the Humanloop API',
    'long_description': None,
    'author': 'Humanloop Team',
    'author_email': 'team@humanloop.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
