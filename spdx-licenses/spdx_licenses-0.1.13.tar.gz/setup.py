# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spdx_licenses']

package_data = \
{'': ['*'], 'spdx_licenses': ['data/*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'beautifulsoup4>=4.11.1,<5.0.0',
 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'spdx-licenses',
    'version': '0.1.13',
    'description': 'A powerful API to grab spdx list licenses, great for boilerplate gen and way more (not official)',
    'long_description': None,
    'author': 'aarmn',
    'author_email': 'aarmn80@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
