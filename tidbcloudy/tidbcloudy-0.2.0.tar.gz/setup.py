# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tidbcloudy', 'tidbcloudy.util']

package_data = \
{'': ['*']}

install_requires = \
['mysqlclient>=2.1.1,<3.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'tidbcloudy',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Aolin',
    'author_email': 'aolinz@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
