# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['syndb_cassandra', 'syndb_cassandra.models', 'syndb_cassandra.utils']

package_data = \
{'': ['*'],
 'syndb_cassandra': ['assets/*', 'assets/neurometa/*'],
 'syndb_cassandra.utils': ['stargate_settings/*']}

install_requires = \
['click>=8.1.3,<9.0.0', 'syndb-admin']

extras_require = \
{'driver': ['cassandra-driver>=3.21.0,<4.0.0',
            'pydantic>=1.9.0,<2.0.0',
            'orjson']}

entry_points = \
{'console_scripts': ['sycass = syndb_cassandra_init.cli:sycass']}

setup_kwargs = {
    'name': 'syndb-cassandra',
    'version': '0.1.2',
    'description': 'Casssandra driver assembly for SynDB',
    'long_description': '# SynapseDB: Cassandra init\n\nThe following scripts initialize the tables used by SynapseDB on the designated Cassandra through CQLSH ',
    'author': 'Can H. Tartanoglu',
    'author_email': 'canhtart@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
