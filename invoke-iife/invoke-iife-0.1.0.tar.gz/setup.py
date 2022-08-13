# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['iife']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'invoke-iife',
    'version': '0.1.0',
    'description': 'Bringing the fun of immediately-invoked function expressions to Python!',
    'long_description': None,
    'author': 'Tor Shepherd',
    'author_email': 'tor.aksel.shepherd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://torshepherd.github.io/iife-py',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
