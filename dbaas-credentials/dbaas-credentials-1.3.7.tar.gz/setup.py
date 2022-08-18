# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbaas_credentials',
 'dbaas_credentials.admin',
 'dbaas_credentials.migrations',
 'dbaas_credentials.service',
 'dbaas_credentials.tests']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dbaas-credentials',
    'version': '1.3.7',
    'description': '',
    'long_description': None,
    'author': 'Mateus Erkmann',
    'author_email': 'mateus.erkmann_esx@prestador.globo',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=2.7,<3.0',
}


setup(**setup_kwargs)
