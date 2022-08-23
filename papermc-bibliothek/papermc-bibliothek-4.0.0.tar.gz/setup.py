# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bibliothek']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.8.2,<3.0.0',
 'typer[all]>=0.6.1,<0.7.0',
 'urllib3>=1.26.12,<2.0.0']

entry_points = \
{'console_scripts': ['bibliothek = bibliothek.__main__:app']}

setup_kwargs = {
    'name': 'papermc-bibliothek',
    'version': '4.0.0',
    'description': 'bibliothek API client with CLI',
    'long_description': None,
    'author': 'Oskar',
    'author_email': '56176746+OskarZyg@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
