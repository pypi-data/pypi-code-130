# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['parkingfunctions']

package_data = \
{'': ['*']}

install_requires = \
['furo>=2022.6.21,<2023.0.0',
 'myst-parser>=0.18.0,<0.19.0',
 'numpy>=1.23.1,<2.0.0',
 'sphinx-rtd-theme>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'parkingfunctions',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Seth Bangert',
    'author_email': 'seth@sbang.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
