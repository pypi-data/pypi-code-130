# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['modelresolvers']

package_data = \
{'': ['*']}

install_requires = \
['flake8', 'pytest', 'strawberry-graphql[debug-server]']

setup_kwargs = {
    'name': 'modelresolvers',
    'version': '0.1.0',
    'description': 'modelresolvers is python package',
    'long_description': None,
    'author': 'Muzaffer Cıkay',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
