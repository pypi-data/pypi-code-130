# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bingus', 'bingus.environ', 'bingus.file']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'bingus',
    'version': '0.2.0',
    'description': 'Many python utilities in one package.',
    'long_description': '# Bingus: the package\n\nBingus is a library of utility scripts and functions.\n',
    'author': 'Bruno Robert',
    'author_email': 'bruno.jeanluke@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/brunorobert/bingus',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
