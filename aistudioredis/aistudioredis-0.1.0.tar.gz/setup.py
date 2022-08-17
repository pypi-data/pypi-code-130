# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aistudioredis']

package_data = \
{'': ['*']}

install_requires = \
['redis>=4.3.4,<5.0.0']

setup_kwargs = {
    'name': 'aistudioredis',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'dashsubhadeep',
    'author_email': 'dash.subhadeep@automationedge.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
