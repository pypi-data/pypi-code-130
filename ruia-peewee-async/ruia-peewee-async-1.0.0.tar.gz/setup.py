# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ruia_peewee_async']

package_data = \
{'': ['*']}

install_requires = \
['peewee-async>=0.8.0,<0.9.0', 'ruia>=0.8.4,<0.9.0']

extras_require = \
{'aiomysql': ['aiomysql>=0.1.1,<0.2.0'], 'aiopg': ['aiopg>=1.3.4,<2.0.0']}

setup_kwargs = {
    'name': 'ruia-peewee-async',
    'version': '1.0.0',
    'description': 'A Ruia plugin that uses the peewee-async to store data to MySQL',
    'long_description': None,
    'author': 'Jack Deng',
    'author_email': 'dlwxxxdlw@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
