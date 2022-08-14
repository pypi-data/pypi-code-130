# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ycache']

package_data = \
{'': ['*']}

install_requires = \
['diskcache>=5.4.0,<6.0.0', 'loguru>=0.6.0,<0.7.0']

setup_kwargs = {
    'name': 'ycache',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'yapex',
    'author_email': 'yapex.yin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
