# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['onchain']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'onchain',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'Erik',
    'author_email': 'erik@zora.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
