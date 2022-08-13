# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydantic_partial']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'pydantic-partial',
    'version': '0.2.0',
    'description': 'Create partial models from your pydantic models. Partial models may allow None for certain or all fields.',
    'long_description': None,
    'author': 'TEAM23 GmbH',
    'author_email': 'info@team23.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/team23/pydantic-partial',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
