# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['syndb_admin']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.2,<2.0.0', 'ruamel.yaml>=0.17.21,<0.18.0']

setup_kwargs = {
    'name': 'syndb-admin',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Can H. Tartanoglu',
    'author_email': '2947298-caniko@users.noreply.gitlab.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
