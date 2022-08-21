# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quasimc']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'quasimc',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Josh Nobus',
    'author_email': 'joshnobus@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
