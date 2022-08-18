# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['divide_stuff']

package_data = \
{'': ['*']}

install_requires = \
['pprintpp>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'divide-stuff',
    'version': '0.1.0',
    'description': 'A very stupid project to learn about how to package apps for PyPy',
    'long_description': None,
    'author': 'Thomas Steck',
    'author_email': 'thomas.steck@ingka.ikea.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
