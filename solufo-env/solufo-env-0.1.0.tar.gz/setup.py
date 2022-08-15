# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['solufo_env']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'solufo-env',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
