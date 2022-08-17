# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pybound']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pybound',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': "Aaron D'Souza",
    'author_email': 'aarondsouz922forrealz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
