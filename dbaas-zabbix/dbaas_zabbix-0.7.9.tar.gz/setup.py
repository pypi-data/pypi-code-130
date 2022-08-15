# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbaas_zabbix']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dbaas-zabbix',
    'version': '0.7.9',
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
