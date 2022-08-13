# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deepdog']

package_data = \
{'': ['*']}

install_requires = \
['numpy==1.22.3', 'pdme>=0.8.6,<0.9.0', 'scipy==1.8.0']

setup_kwargs = {
    'name': 'deepdog',
    'version': '0.6.4',
    'description': '',
    'long_description': None,
    'author': 'Deepak Mallubhotla',
    'author_email': 'dmallubhotla+github@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
