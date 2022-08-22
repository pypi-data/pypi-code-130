# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flow360']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'flow360',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'An Li',
    'author_email': 'kidylee@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
