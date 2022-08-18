# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['databusclient']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0', 'typer>=0.6.1,<0.7.0']

setup_kwargs = {
    'name': 'databusclient',
    'version': '0.8',
    'description': 'A simple client for submitting data to the databus',
    'long_description': None,
    'author': 'DBpedia Association',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
