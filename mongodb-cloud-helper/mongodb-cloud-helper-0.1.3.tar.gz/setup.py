# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mongodb_cloud_helper', 'mongodb_cloud_helper.svc']

package_data = \
{'': ['*']}

install_requires = \
['baseblock', 'pymongo>=4.1.0,<5.0.0']

setup_kwargs = {
    'name': 'mongodb-cloud-helper',
    'version': '0.1.3',
    'description': 'Helper Microservice when a MongoDB Cloud instance is required.',
    'long_description': None,
    'author': 'Craig Trim',
    'author_email': 'craigtrim@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '==3.8.5',
}


setup(**setup_kwargs)
