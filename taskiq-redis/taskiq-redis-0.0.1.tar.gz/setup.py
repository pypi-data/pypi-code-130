# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taskiq_redis', 'taskiq_redis.tests']

package_data = \
{'': ['*']}

install_requires = \
['redis>=4.2.0,<5.0.0', 'taskiq>=0,<1']

setup_kwargs = {
    'name': 'taskiq-redis',
    'version': '0.0.1',
    'description': 'Redis integration for taskiq',
    'long_description': None,
    'author': 'taskiq-team',
    'author_email': 'taskiq@norely.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
