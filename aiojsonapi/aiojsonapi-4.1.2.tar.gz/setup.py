# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiojsonapi']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0']

setup_kwargs = {
    'name': 'aiojsonapi',
    'version': '4.1.2',
    'description': 'JSON aiohttp API constructor',
    'long_description': None,
    'author': 'Yurzs',
    'author_email': 'yury@yurzs.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
