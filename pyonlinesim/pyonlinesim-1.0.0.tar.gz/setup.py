# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyonlinesim',
 'pyonlinesim.core',
 'pyonlinesim.core.abc',
 'pyonlinesim.core.methods',
 'pyonlinesim.exceptions',
 'pyonlinesim.types']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.3', 'pydantic>=1.9.2,<2.0.0']

setup_kwargs = {
    'name': 'pyonlinesim',
    'version': '1.0.0',
    'description': 'Asynchronous wrapper to interact with onlinesim.ru API',
    'long_description': '# pyonlinesim',
    'author': 'Marple',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/marple-git/pyonlinesim',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
