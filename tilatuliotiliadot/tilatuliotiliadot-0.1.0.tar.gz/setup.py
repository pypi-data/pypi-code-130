# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tilatuliotiliadot']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tilatuliotiliadot',
    'version': '0.1.0',
    'description': 'wait for next',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
