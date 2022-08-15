# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dvartk']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.3,<4.0.0',
 'numpy>=1.21.6,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pyfaidx>=0.7.1,<0.8.0',
 'seaborn>=0.11.2,<0.12.0',
 'wgs-analysis>=0.0.3,<0.0.4']

setup_kwargs = {
    'name': 'dvartk',
    'version': '0.1.5',
    'description': 'A variant comparison toolkit',
    'long_description': None,
    'author': 'Seongmin Choi',
    'author_email': 'soymintc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
