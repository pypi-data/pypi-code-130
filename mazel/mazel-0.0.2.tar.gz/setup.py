# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mazel', 'mazel.commands', 'mazel.contrib', 'mazel.runtimes']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'ruamel.yaml>=0.16.10,<0.17.0',
 'tomlkit>=0.11.0,<0.12.0']

entry_points = \
{'console_scripts': ['mazel = mazel.main:cli']}

setup_kwargs = {
    'name': 'mazel',
    'version': '0.0.2',
    'description': 'A simple bazel-inspired Makefile runner for monorepos',
    'long_description': None,
    'author': 'John Paulett',
    'author_email': 'john.paulett@equium.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/equium-io/mazel',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
