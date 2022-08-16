# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['idd']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'idd',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'sea-wyq',
    'author_email': '3236961631@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
