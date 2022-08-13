# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbrep']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dbrep',
    'version': '0.0.4',
    'description': 'Package to sync tables across DBs, i.e. EL in ELT/ETL',
    'long_description': '# dbrep\nPackage to sync tables across DBs, i.e. EL in ELT/ETL\n',
    'author': 'Valentin  Stepanovich',
    'author_email': 'kolhizin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
