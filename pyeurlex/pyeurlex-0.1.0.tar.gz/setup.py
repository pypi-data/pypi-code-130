# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eurlex']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0',
 'fire>=0.4.0,<0.5.0',
 'halo>=0.0.31,<0.0.32',
 'lxml>=4.9.1,<5.0.0',
 'pandas>=1.4.3,<2.0.0',
 'requests>=2.28.1,<3.0.0',
 'sparql-dataframe>=0.4,<0.5']

setup_kwargs = {
    'name': 'pyeurlex',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'step21',
    'author_email': 'step21@devtal.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
